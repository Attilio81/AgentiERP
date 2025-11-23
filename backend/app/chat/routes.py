"""
Chat routes for agent interactions.
Includes SSE streaming endpoint and conversation management.
"""
import json
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Dict
from datetime import datetime
from datapizza.core.clients import ClientResponse
from app.database.database import get_db
from app.database.models import Conversation, Message
from app.auth.middleware import get_current_user
from app.agents.manager import get_agent_manager
from app.config import get_settings
from app.llm.factory import LLMConfigurationError, build_llm_client

router = APIRouter(prefix="/api/chat", tags=["Chat"])


class ChatRequest(BaseModel):
    """Chat request model."""
    agent_name: str = Field(..., description="Nome dell'agente da utilizzare")
    message: str = Field(..., min_length=1, description="Messaggio da inviare all'agente")
    conversation_id: int | None = Field(None, description="ID conversazione esistente (opzionale)")


class AgentInfo(BaseModel):
    """Agent information model."""
    name: str
    description: str


class ConversationResponse(BaseModel):
    """Conversation response model."""
    id: int
    agent_name: str
    title: str | None
    created_at: datetime
    updated_at: datetime


class MessageResponse(BaseModel):
    """Message response model."""
    id: int
    role: str
    content: str
    timestamp: datetime


class FAQItem(BaseModel):
    """FAQ item model."""
    question: str
    answer: str


@router.get("/agents", response_model=List[AgentInfo])
def list_agents() -> List[AgentInfo]:
    """
    Get list of available agents.
    
    Returns list of agents with their names and descriptions.
    No authentication required for this endpoint.
    """
    agent_manager = get_agent_manager()
    agents_dict = agent_manager.list_agents()
    
    return [
        AgentInfo(name=name, description=desc)
        for name, desc in agents_dict.items()
    ]


@router.post("/stream")
async def chat_stream(
    request: ChatRequest,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Stream chat responses from an agent using Server-Sent Events.
    
    This endpoint establishes an SSE connection and streams the agent's
    response in real-time as it's generated.
    """
    agent_manager = get_agent_manager()
    
    # Validate agent exists
    if not agent_manager.agent_exists(request.agent_name):
        raise HTTPException(
            status_code=400,
            detail=f"Agente '{request.agent_name}' non trovato."
        )
    
    # Get or create conversation
    if request.conversation_id:
        conversation = db.query(Conversation).filter(
            Conversation.id == request.conversation_id,
            Conversation.user_id == user_id
        ).first()
        
        if not conversation:
            raise HTTPException(
                status_code=404,
                detail="Conversazione non trovata."
            )
    else:
        # Create new conversation
        conversation = Conversation(
            user_id=user_id,
            agent_name=request.agent_name,
            title=request.message[:50] if len(request.message) > 50 else request.message
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
    
    # Save user message
    user_message = Message(
        conversation_id=conversation.id,
        role="user",
        content=request.message
    )
    db.add(user_message)
    db.commit()
    
    # Get agent and stream response
    agent = agent_manager.get_agent(request.agent_name)

    async def event_generator():
        """
        Genera eventi Server-Sent Events (SSE) dalla risposta dell'agente.

        Flusso:
        1. Invia conversation_id al client
        2. Recupera cronologia conversazione dal DB (per memory)
        3. Esegue agent.a_run() passando lo storico messaggi
        4. Invia la risposta completa al client
        5. Salva risposta nel DB
        6. Invia segnale di completamento

        Yields:
            Eventi SSE in formato: data: {"type": "...", ...}\n\n
        """
        try:
            # Send conversation ID first
            yield f"data: {{\"type\": \"conversation_id\", \"id\": {conversation.id}}}\n\n"

            # ========================================
            # MEMORY: Recupera cronologia conversazione
            # ========================================
            # Per consentire all'agente di mantenere il contesto, recuperiamo
            # tutti i messaggi precedenti della conversazione corrente e li
            # passiamo all'agente nel formato richiesto da Datapizza.

            previous_messages = (
                db.query(Message)
                .filter(Message.conversation_id == conversation.id)
                .filter(Message.id != user_message.id)  # Escludi il messaggio appena aggiunto
                .order_by(Message.timestamp.asc())
                .all()
            )

            # ========================================
            # MEMORY: Costruisci cronologia usando Datapizza Memory class
            # ========================================
            # Datapizza Agent supporta conversational memory attraverso la classe Memory.
            # Creiamo una Memory instance per questa conversazione e la popoliamo
            # con la cronologia precedente.

            from datapizza.memory import Memory
            from datapizza.type import ROLE, TextBlock

            # Crea Memory instance per questa conversazione
            conversation_memory = Memory()

            # Popola memory con cronologia precedente
            for msg in previous_messages:
                # Valida ruolo
                if msg.role not in ("user", "assistant"):
                    print(f"[WARN] Skipping message with invalid role: {msg.role}")
                    continue

                # Valida contenuto non vuoto
                if not msg.content or not msg.content.strip():
                    print(f"[WARN] Skipping message with empty content")
                    continue

                # Valida alternanza: controlla se l'ultimo turno ha lo stesso ruolo
                if len(conversation_memory) > 0:
                    # Ottieni ultimo turno e verifica ruolo
                    # Memory.__len__ ritorna il numero di turni
                    # Evitiamo di aggiungere due turni consecutivi dello stesso ruolo
                    last_turn_blocks = conversation_memory[-1]
                    if last_turn_blocks:
                        # Assumiamo che tutti i blocchi in un turno abbiano lo stesso ruolo
                        # Per semplicità, saltiamo se il ruolo corrisponde al precedente
                        prev_role = "assistant" if msg.role == "user" else "user"
                        # Nota: questa è una semplificazione, idealmente dovremmo controllare
                        # il ruolo effettivo dell'ultimo turno, ma Memory non espone facilmente questa info

                # Aggiungi turno alla Memory
                role = ROLE.USER if msg.role == "user" else ROLE.ASSISTANT
                try:
                    conversation_memory.add_turn(
                        TextBlock(content=msg.content),
                        role=role
                    )
                except Exception as e:
                    print(f"[ERROR] Failed to add turn to memory: {e}")
                    continue

            # Log della dimensione dello storico (per debugging)
            print(f"[chat_stream] Conversation {conversation.id}: {len(conversation_memory)} previous turns in memory")

            # ========================================
            # AGENT EXECUTION CON MEMORY
            # ========================================
            # Esegui l'agente passando:
            # - Il nuovo messaggio utente
            # - Lo storico conversazione (messages=history) per la memory
            #
            # NOTA: Datapizza Agent usa 'messages' per il contesto conversazionale.
            # Questo permette all'agente di:
            # - Fare riferimento a query precedenti
            # - Continuare analisi multi-step
            # - Mantenere coerenza nelle risposte
            #
            # IMPORTANTE: Se non c'è cronologia (lista vuota), non passiamo il parametro
            # 'messages' per evitare errori "at least one message is required" dall'API LLM.

            # Esegui agente con Memory
            # Datapizza Agent supporta il parametro 'memory' (non 'messages'!)
            # Memory deve essere passata come oggetto Memory, non come lista di messaggi
            try:
                if len(conversation_memory) > 0:
                    # C'è cronologia: passa Memory object
                    print(f"[chat_stream] Executing agent with {len(conversation_memory)} turns of memory")
                    result = await agent.a_run(request.message, memory=conversation_memory)
                else:
                    # Nessuna cronologia: esecuzione semplice
                    print("[chat_stream] Executing agent without memory (first message)")
                    result = await agent.a_run(request.message)
            except TypeError as e:
                # Fallback: se agent non supporta memory parameter, prova senza
                print(f"[chat_stream] WARN: Agent.a_run() doesn't support 'memory' parameter: {e}")
                print("[chat_stream] Falling back to execution without memory")
                result = await agent.a_run(request.message)

            # Extract full response text
            if hasattr(result, "text") and getattr(result, "text", None):
                full_response = result.text
            elif isinstance(result, str):
                full_response = result
            else:
                full_response = str(result) if result is not None else ""

            # Debug: log generated response (truncated)
            print("[chat_stream] full_response length:", len(full_response))
            print("[chat_stream] full_response preview:", repr(full_response[:300]))

            # Escape newlines and quotes for JSON
            content_escaped = (
                full_response
                .replace('\\', '\\\\')
                .replace('"', '\\"')
                .replace('\n', '\\n')
            )
            # Send a single content event with the full answer
            yield f'data: {{"type": "content", "content": "{content_escaped}"}}\n\n'
            
            # Save assistant message
            assistant_message = Message(
                conversation_id=conversation.id,
                role="assistant",
                content=full_response
            )
            db.add(assistant_message)
            
            # Update conversation timestamp
            conversation.updated_at = datetime.utcnow()
            db.commit()
            
            # Send completion signal
            yield 'data: {"type": "done"}\n\n'
            
        except Exception as e:
            error_msg = str(e).replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
            yield f'data: {{\"type\": \"error\", \"error\": "{error_msg}"}}\n\n'
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable nginx buffering
        }
    )


@router.get("/conversations", response_model=List[ConversationResponse])
def get_conversations(
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> List[ConversationResponse]:
    """
    Get all conversations for the current user.
    
    Returns conversations ordered by most recent first.
    """
    conversations = db.query(Conversation).filter(
        Conversation.user_id == user_id
    ).order_by(Conversation.updated_at.desc()).all()
    
    return conversations


@router.get("/conversations/{conversation_id}/messages", response_model=List[MessageResponse])
def get_conversation_messages(
    conversation_id: int,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> List[MessageResponse]:
    """
    Get all messages for a specific conversation.
    
    Returns messages ordered chronologically.
    """
    # Verify conversation belongs to user
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == user_id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=404,
            detail="Conversazione non trovata."
        )
    
    messages = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.timestamp.asc()).all()
    
    return messages


@router.get("/faq_suggestions", response_model=List[FAQItem])
def get_faq_suggestions(
    agent_name: str,
    limit: int = 50,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> List[FAQItem]:
    """Generate FAQ suggestions for the given agent based on user's recent questions."""
    # Clamp limit to a reasonable range
    if limit <= 0:
        return []
    max_limit = 100
    limit = min(limit, max_limit)

    # Collect recent user questions for this agent
    rows = (
        db.query(Message.content)
        .join(Conversation, Message.conversation_id == Conversation.id)
        .filter(
            Conversation.user_id == user_id,
            Conversation.agent_name == agent_name,
            Message.role == "user",
        )
        .order_by(Message.timestamp.desc())
        .limit(limit)
        .all()
    )

    questions = [row[0].strip() for row in rows if row[0]]
    if not questions:
        return []

    # Oldest questions first in the prompt for better context
    questions_block_lines = [f"- {q}" for q in reversed(questions)]
    questions_block = "\n".join(questions_block_lines)

    settings = get_settings()
    try:
        client = build_llm_client(settings, use_case="faq")
    except LLMConfigurationError as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )

    prompt = (
        f'Sei un assistente che genera FAQ in italiano per l\'agente "{agent_name}" '
        "di un sistema di analytics su SQL Server.\n\n"
        "Ti fornisco un elenco di domande reali poste dall'utente. Il tuo compito è:\n"
        "1. Raggruppare le domande simili.\n"
        "2. Estrarre al massimo 10 FAQ rappresentative.\n"
        "3. Per ogni FAQ scrivi:\n"
        '   - "question": una domanda SECCA e completa, già pronta da usare così com\'è, senza segnaposto o parti da sostituire. Ad esempio: scrivi "Quali sono gli articoli più venduti nel 2025?" e NON "Quali sono gli articoli più venduti in un determinato anno?".\n'
        '   - "answer": opzionale; se non hai nulla di utile da aggiungere, usa semplicemente una stringa vuota "" (non spiegare o commentare la domanda).\n\n'
        "IMPORTANTE:\n"
        '- Le domande NON devono contenere placeholder come "<anno>", "[cliente]", "in un determinato anno", ecc.\n'
        '- Rispondi SOLO in formato JSON valido.\n'
        '- Il JSON dev\'essere una lista di oggetti con chiavi "question" e "answer".\n'
        "- Non aggiungere testo prima o dopo il JSON, nessun commento, nessun markdown.\n\n"
        "Domande recenti (dalla più vecchia alla più recente):\n"
        f"{questions_block}\n"
    )

    try:
        raw_response = client.invoke(prompt)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Errore durante la generazione delle FAQ: {str(e)}",
        )

    def _extract_faq_text(result) -> str:
        if isinstance(result, ClientResponse):
            text = getattr(result, "text", None)
            if not text and hasattr(result, "completion"):
                text = getattr(result, "completion", None)
            if text is not None:
                return str(text)
        if isinstance(result, str):
            return result
        return str(result) if result is not None else ""

    def _parse_faq_response(text: str) -> List[FAQItem]:
        if not text:
            return []

        candidates: List[dict] = []

        # First, try to parse the whole string as JSON
        try:
            data = json.loads(text)
            if isinstance(data, list):
                candidates = data
            else:
                return []
        except json.JSONDecodeError:
            # Try to extract a JSON array substring
            start = text.find("[")
            end = text.rfind("]")
            if start != -1 and end != -1 and end > start:
                try:
                    data = json.loads(text[start : end + 1])
                    if isinstance(data, list):
                        candidates = data
                except json.JSONDecodeError:
                    return []

        faqs: List[FAQItem] = []
        for item in candidates:
            if not isinstance(item, dict):
                continue
            question = (item.get("question") or "").strip()
            answer = (item.get("answer") or "").strip()
            # Accettiamo anche answer vuota: l'importante è avere una domanda pulita
            if question:
                faqs.append(FAQItem(question=question, answer=answer))

        return faqs

    response_text = _extract_faq_text(raw_response)

    # Debug: log a preview of the raw model response
    try:
        print("[faq_suggestions] raw model response preview:", repr(response_text[:500]))
    except Exception:
        pass

    faqs = _parse_faq_response(response_text)

    # Fallback: if parsing fails or returns no FAQ, use recent questions as FAQ
    if not faqs:
        print("[faq_suggestions] No FAQ parsed from model response, using fallback questions.")
        fallback: List[FAQItem] = []
        max_fallback = 10
        for q in questions:
            q_clean = q.strip()
            if not q_clean:
                continue
            if len(q_clean) > 200:
                q_clean = q_clean[:200]
            fallback.append(FAQItem(question=q_clean, answer=""))
            if len(fallback) >= max_fallback:
                break
        faqs = fallback

    return faqs
