"""
Agent Manager using datapizza-ai framework.
Gestisce agenti completamente configurati da database (chat_ai.agents).

Questo modulo è responsabile di:
- Caricare la configurazione degli agenti dal database
- Creare istanze di Agent Datapizza con tools e memory
- Gestire il lifecycle degli agenti (init, reinit)
- Fornire accesso thread-safe agli agenti tramite singleton pattern
"""
from typing import Dict, List

from datapizza.agents import Agent
from datapizza.tools.duckduckgo import DuckDuckGoSearchTool

from app.agents.sql_tools import create_sql_select_tool, create_get_schema_tool
from app.config import Settings
from app.database.database import SessionLocal
from app.database.models import AgentConfig
from app.llm.factory import LLMConfigurationError, build_llm_client


class AgentManager:
    """
    Gestisce agenti Datapizza definiti dinamicamente da database.
    Ogni riga in chat_ai.agents rappresenta un agente potenziale.
    """
    
    def __init__(self, settings: Settings):
        """
        Initialize all agents with their respective tools and prompts.
        Gli agenti vengono creati leggendo la configurazione da chat_ai.agents.
        """
        self.settings = settings
        self.agents: Dict[str, Agent] = {}
        
        # Create default LLM client (shared by agents unless overridden)
        try:
            self.default_client = build_llm_client(settings, use_case="agent")
        except LLMConfigurationError as exc:  # pragma: no cover - startup failure
            raise RuntimeError(f"Configurazione LLM non valida: {exc}") from exc
        
        # Initialize agents from DB configuration
        self._init_agents_from_db()

    def _resolve_tools(self, agent_config: AgentConfig) -> List:
        """
        Risolve i tool da assegnare all'agente basandosi sulla configurazione DB.

        Questo metodo implementa un registry pattern: ogni tool_id viene mappato
        alla corrispondente factory function che crea il tool vero e proprio.

        Args:
            agent_config: Configurazione agente dal database (tabella chat_ai.agents)

        Returns:
            Lista di tool callables pronti per essere passati all'Agent Datapizza

        Note:
            I tool disponibili sono definiti nella colonna 'tool_names' come CSV:
            Esempio: "sql_select,get_schema"
        """
        tools: List = []
        db_uri = agent_config.db_uri  # Connessione DB specifica per questo agente
        schema_name = agent_config.schema_name  # Schema SQL da esplorare (es. 'dbo', 'magazzino')

        # Parse della lista di tool dalla configurazione DB
        if agent_config.tool_names:
            tool_ids = [t.strip().lower() for t in agent_config.tool_names.split(",") if t.strip()]
        else:
            tool_ids = []

        # Registry: mappa tool_id → factory function
        for tool_id in tool_ids:
            if tool_id == "sql_select":
                # Tool per eseguire query SELECT sul database
                tools.append(create_sql_select_tool(agent_config.name, db_uri))

            elif tool_id == "get_schema":
                # Tool per esplorare schema database (tabelle, colonne)
                # NUOVO: permette agli agenti di scoprire autonomamente lo schema
                tools.append(create_get_schema_tool(agent_config.name, db_uri, schema_name))

            elif tool_id == "duckduckgo" or tool_id == "web_search":
                # Tool per ricerca web (DuckDuckGo)
                tools.append(DuckDuckGoSearchTool())

            # Spazio per futuri tool:
            # elif tool_id == "document_reader":
            #     tools.append(create_document_reader_tool())

        return tools

    def _init_agents_from_db(self) -> None:
        """
        Inizializza tutti gli agenti attivi leggendo la configurazione dal database.

        Questo metodo:
        1. Legge la tabella chat_ai.agents per trovare agenti attivi
        2. Per ogni agente, risolve i tools configurati
        3. Costruisce il system prompt completo
        4. Crea l'istanza Agent Datapizza con memory integrata
        5. Registra l'agente nel registry interno (self.agents)

        Note:
            - Gli agenti con is_active=False vengono ignorati
            - Se un agente non ha tools validi, viene skippato
            - Ogni agente può avere il proprio modello LLM e connessione DB
        """
        self.agents = {}
        db = SessionLocal()
        try:
            # Query agenti attivi dal database
            db_agents = (
                db.query(AgentConfig)
                .filter(AgentConfig.is_active == True)  # Solo agenti attivi
                .order_by(AgentConfig.name.asc())
                .all()
            )

            for db_agent in db_agents:
                # 1. RISOLUZIONE TOOLS
                tools = self._resolve_tools(db_agent)

                # Se non sono configurati tools validi, saltiamo l'agente
                # (un agente senza tools non può fare nulla di utile)
                if not tools:
                    print(f"[AgentManager] Agente '{db_agent.name}' skippato: nessun tool valido configurato")
                    continue

                # 2. COSTRUZIONE SYSTEM PROMPT
                base_prompt = db_agent.system_prompt or ""

                # Suffix generico per tutti gli agenti: impone uno stile di risposta finale
                # orientato ai risultati, non al piano di azione.
                response_suffix = (
                    "\n\n"  # separatore sicuro
                    "REGOLE GENERALI PER LA RISPOSTA FINALE:\n"
                    "- Dopo aver usato i tools, parla come se l'analisi fosse già stata eseguita.\n"
                    "- NON usare frasi come 'analizzerò', 'vado a verificare', 'interrogherò i dati'.\n"
                    "- Riassumi sempre cosa mostrano i risultati delle query, citando almeno 1-2 numeri o valori chiave.\n"
                    "- Quando viene richiesto un TOP N, mostra TUTTI gli N elementi in formato tabella.\n"
                )

                system_prompt = f"{base_prompt}{response_suffix}" if base_prompt else response_suffix

                # 3. CREAZIONE CLIENT LLM
                # Ogni agente può avere il proprio modello (override), altrimenti usa quello di default
                if db_agent.model:
                    try:
                        agent_client = build_llm_client(
                            self.settings,
                            use_case="agent",
                            model_override=db_agent.model,
                        )
                    except LLMConfigurationError as exc:
                        print(
                            f"[AgentManager] Ignoro agente {db_agent.name}: {exc}"
                        )
                        continue
                else:
                    agent_client = self.default_client

                # 4. CREAZIONE AGENT CON MEMORY
                # NOTA: Datapizza Agent gestisce automaticamente la memoria conversazionale
                # attraverso il parametro 'messages' passato in .run() o .a_run()
                # Non serve una Memory esplicita qui, ma la gestiamo passando lo storico
                # nel chat/routes.py quando chiamiamo agent.a_run()

                self.agents[db_agent.name] = Agent(
                    name=db_agent.name,
                    client=agent_client,
                    system_prompt=system_prompt,
                    tools=tools,
                    # NOTA IMPORTANTE SULLA MEMORY:
                    # Datapizza Agent supporta memory conversazionale tramite il parametro
                    # 'messages' nella chiamata .run() o .a_run().
                    # Non serve un oggetto Memory separato - la storia viene passata
                    # direttamente come lista di messaggi dal chiamante (chat/routes.py).
                    #
                    # Esempio di uso in chat/routes.py:
                    # history = [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
                    # result = await agent.a_run(new_message, messages=history)
                )

                print(f"[AgentManager] Agente '{db_agent.name}' inizializzato con {len(tools)} tools")

        finally:
            db.close()
    
    def get_agent(self, agent_name: str) -> Agent:
        """
        Get an agent by name.
        
        Args:
            agent_name: Name of the agent ('magazzino', 'ordini', or 'vendite')
            
        Returns:
            Agent instance
            
        Raises:
            ValueError: If agent_name is not found
        """
        if agent_name not in self.agents:
            raise ValueError(
                f"Agent '{agent_name}' non trovato. "
                f"Agenti disponibili: {list(self.agents.keys())}"
            )
        return self.agents[agent_name]
    
    def list_agents(self) -> Dict[str, str]:
        """
        Get list of available agents with their descriptions.
        
        Returns:
            Dictionary mapping agent names to descriptions
        """
        if not self.agents:
            return {}

        db = SessionLocal()
        try:
            result: Dict[str, str] = {}
            names = list(self.agents.keys())

            db_agents = (
                db.query(AgentConfig)
                .filter(AgentConfig.name.in_(names))
                .order_by(AgentConfig.name.asc())
                .all()
            )

            for db_agent in db_agents:
                result[db_agent.name] = db_agent.description or db_agent.name

            # Per eventuali agenti senza riga in tabella, usiamo il nome come descrizione
            for name in names:
                if name not in result:
                    result[name] = name

            return result

        except Exception:
            # In caso di errore DB, esponiamo comunque gli agenti correnti con nome base
            return {name: name for name in self.agents.keys()}
        finally:
            db.close()
    
    def agent_exists(self, agent_name: str) -> bool:
        """
        Check if an agent exists.
        
        Args:
            agent_name: Name of the agent to check
            
        Returns:
            True if agent exists, False otherwise
        """
        return agent_name in self.agents


# Global agent manager instance (initialized on app startup)
_agent_manager: AgentManager = None


def get_agent_manager() -> AgentManager:
    """
    Get the global agent manager instance.
    
    Returns:
        AgentManager instance
        
    Raises:
        RuntimeError: If agent manager is not initialized
    """
    if _agent_manager is None:
        raise RuntimeError("AgentManager non inizializzato. Chiamare init_agent_manager() prima.")
    return _agent_manager


def init_agent_manager(settings: Settings):
    """
    Initialize the global agent manager.
    Should be called once during app startup.
    
    Args:
        settings: Application settings
    """
    global _agent_manager
    _agent_manager = AgentManager(settings)
