"""
Agent Manager using datapizza-ai framework.
Gestisce agenti completamente configurati da database (chat_ai.agents).
"""
from typing import Dict, List
from datapizza.agents import Agent
from app.agents.client_wrapper import RetryAnthropicClient
from app.agents.sql_tools import create_sql_select_tool
from app.config import Settings
from app.database.database import SessionLocal
from app.database.models import AgentConfig


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
        
        # Create Anthropic client (shared by all agents)
        # Uses RetryAnthropicClient to handle 529 Overloaded errors
        self.client = RetryAnthropicClient(
            api_key=settings.anthropic_api_key,
            model=settings.agent_model
        )
        
        # Initialize agents from DB configuration
        self._init_agents_from_db()

    def _resolve_tools(self, agent_config: AgentConfig) -> List:
        """Resolve tool callables for a given agent configuration."""
        tools: List = []
        db_uri = agent_config.db_uri

        if agent_config.tool_names:
            tool_ids = [t.strip().lower() for t in agent_config.tool_names.split(",") if t.strip()]
        else:
            tool_ids = []

        for tool_id in tool_ids:
            if tool_id == "sql_select":
                tools.append(create_sql_select_tool(agent_config.name, db_uri))

        return tools

    def _init_agents_from_db(self) -> None:
        """Initialize all active agents from chat_ai.agents configuration."""
        self.agents = {}
        db = SessionLocal()
        try:
            db_agents = (
                db.query(AgentConfig)
                .filter(AgentConfig.is_active == True)
                .order_by(AgentConfig.name.asc())
                .all()
            )

            for db_agent in db_agents:
                tools = self._resolve_tools(db_agent)
                # Se non sono configurati tools validi, saltiamo l'agente
                if not tools:
                    continue

                base_prompt = db_agent.system_prompt or ""

                # Suffix generico per tutti gli agenti: impone uno stile di risposta finale
                # orientato ai risultati, non al piano di azione.
                response_suffix = (
                    "\n\n"  # separatore sicuro
                    "REGOLE GENERALI PER LA RISPOSTA FINALE:\n"
                    "- Dopo aver usato i tools, parla come se l'analisi fosse già stata eseguita.\n"
                    "- NON usare frasi come 'analizzerò', 'vado a verificare', 'interrogherò i dati'.\n"
                    "- Riassumi sempre cosa mostrano i risultati delle query, citando almeno 1-2 numeri o valori chiave.\n"
                )

                system_prompt = f"{base_prompt}{response_suffix}" if base_prompt else response_suffix

                self.agents[db_agent.name] = Agent(
                    name=db_agent.name,
                    client=self.client,
                    system_prompt=system_prompt,
                    tools=tools,
                )

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
