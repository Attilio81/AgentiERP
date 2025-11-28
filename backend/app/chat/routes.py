"""
Chat routes for agent interactions.
Includes SSE streaming endpoint and conversation management.
"""
import json
import httpx
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime
from datapizza.core.clients import ClientResponse
from app.database.database import get_db
from app.database.models import Conversation, Message
from app.auth.middleware import get_current_user
from app.agents.manager import get_agent_manager
from app.config import get_settings
from app.llm.factory import LLMConfigurationError, build_llm_client

# Configurazione memoria conversazionale
SLIDING_WINDOW_SIZE = 2  # Ultimi N messaggi da mantenere completi (2 = ultimo scambio)


async def summarize_with_local_llm(messages: List[Dict[str, str]]) -> Optional[str]:
    """
    Riassume i messaggi vecchi usando LLM locale (LM Studio).
    Usa la configurazione da settings.
    Ritorna None se non disponibile.
    """
    if not messages:
        return None
    
    settings = get_settings()
    
    # Formatta i messaggi per il riassunto
    text = "\n".join([
        f"{'Utente' if m['role'] == 'user' else 'Assistente'}: {m['content'][:200]}"
        for m in messages
    ])
    
    prompt = f"""Riassumi questa conversazione in 2-3 frasi brevissime.
MANTIENI SOLO: nomi prodotti, codici articolo, fornitori, quantità, numeri chiave.
ESCLUDI: schemi database, nomi colonne, dettagli tecnici SQL, tabelle complete.

{text}

Riassunto conciso:"""

    # Usa modello leggero se configurato, altrimenti modello principale
    model = settings.local_llm_light_model or settings.local_llm_model
    
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            # LM Studio (OpenAI-compatibile)
            response = await client.post(
                settings.local_llm_url,
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3,
                    "max_tokens": 150
                }
            )
            if response.status_code == 200:
                result = response.json()["choices"][0]["message"]["content"].strip()
                print(f"[LM Studio] Riassunto ({model}): {result[:100]}...")
                return result
            else:
                print(f"[LM Studio] Errore {response.status_code}: {response.text[:200]}")
    except Exception as e:
        print(f"[LM Studio] Non disponibile: {e}")
    
    return None

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
            # SLIDING WINDOW + RIASSUNTO OLLAMA
            # ========================================
            # Con stateless=True, gestiamo la memoria esternamente:
            # 1. Messaggi vecchi → Riassunto con Ollama (se disponibile)
            # 2. Ultimi N messaggi → Completi nel contesto
            # 3. Messaggio attuale → Domanda dell'utente
            
            # Converti messaggi DB in lista dict
            all_messages = [
                {"role": msg.role, "content": msg.content}
                for msg in previous_messages
            ]
            
            # Costruisci contesto ottimizzato
            context_parts = []
            
            if len(all_messages) > SLIDING_WINDOW_SIZE:
                # Messaggi vecchi da riassumere
                old_messages = all_messages[:-SLIDING_WINDOW_SIZE]
                recent_messages = all_messages[-SLIDING_WINDOW_SIZE:]
                
                # Prova a riassumere con LLM locale (LM Studio o Ollama)
                summary = await summarize_with_local_llm(old_messages)
                if summary:
                    context_parts.append(f"RIASSUNTO CONVERSAZIONE PRECEDENTE:\n{summary}")
                else:
                    # Fallback: tronca messaggi vecchi
                    for msg in old_messages[-2:]:  # Solo ultimi 2 dei vecchi
                        role = "UTENTE" if msg["role"] == "user" else "ASSISTENTE"
                        content = msg["content"][:150] + "..." if len(msg["content"]) > 150 else msg["content"]
                        context_parts.append(f"{role}: {content}")
                
                # Aggiungi messaggi recenti completi
                context_parts.append("\nULTIMI MESSAGGI:")
                for msg in recent_messages:
                    role = "UTENTE" if msg["role"] == "user" else "ASSISTENTE"
                    content = msg["content"][:500] + "..." if len(msg["content"]) > 500 else msg["content"]
                    context_parts.append(f"{role}: {content}")
            else:
                # Pochi messaggi: includi tutti
                for msg in all_messages:
                    role = "UTENTE" if msg["role"] == "user" else "ASSISTENTE"
                    content = msg["content"][:500] + "..." if len(msg["content"]) > 500 else msg["content"]
                    context_parts.append(f"{role}: {content}")
            
            # Costruisci messaggio augmented
            if context_parts:
                context_str = "\n".join(context_parts)
                augmented_message = f"""CONTESTO CONVERSAZIONE:
{context_str}

DOMANDA ATTUALE:
{request.message}"""
                print(f"[chat_stream] Context: {len(all_messages)} msgs, sliding window applied")
            else:
                augmented_message = request.message
                print(f"[chat_stream] No context (first message)")
            
            # Esegui agent
            print(f"[chat_stream] Executing agent...")
            try:
                result = await agent.a_run(augmented_message)
            except Exception as e:
                print(f"[chat_stream] ERROR during agent execution: {e}")
                import traceback
                traceback.print_exc()
                raise

            # Extract full response text
            if hasattr(result, "text") and result.text:
                full_response = result.text
            elif isinstance(result, str):
                full_response = result
            else:
                full_response = str(result) if result is not None else ""
            
            # Rimuovi i JSON dei tool_call/tool_result dalla risposta (se presenti)
            # Questi non devono essere mostrati all'utente
            def clean_tool_json(text: str) -> str:
                """Rimuove le righe che contengono JSON di tool_call o tool_result."""
                lines = text.split('\n')
                cleaned_lines = []
                for line in lines:
                    stripped = line.strip()
                    # Salta righe che sono JSON di tool calls
                    if stripped.startswith('{"type":') and ('"tool_call"' in stripped or '"tool_result"' in stripped):
                        continue
                    cleaned_lines.append(line)
                return '\n'.join(cleaned_lines)
            
            full_response = clean_tool_json(full_response)
            # Rimuovi linee vuote multiple
            import re
            full_response = re.sub(r'\n{3,}', '\n\n', full_response).strip()

            # Token usage tracking
            if hasattr(result, "usage") and result.usage:
                usage = result.usage
                prompt_tokens = getattr(usage, "prompt_tokens", 0) or getattr(usage, "input_tokens", 0) or 0
                completion_tokens = getattr(usage, "completion_tokens", 0) or getattr(usage, "output_tokens", 0) or 0
                total_tokens = prompt_tokens + completion_tokens
                print(f"[TOKENS] Prompt: {prompt_tokens}, Completion: {completion_tokens}, Total: {total_tokens}")

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
