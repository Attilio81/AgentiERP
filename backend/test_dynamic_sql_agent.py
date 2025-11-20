import asyncio

from datapizza.agents import Agent
from datapizza.tools.SQLDatabase import SQLDatabase

from app.config import get_settings
from app.agents.client_wrapper import RetryAnthropicClient


async def main() -> None:
    """Prototipo di agente Datapizza che usa SQLDatabase contro il DB reale.

    Questo script è separato dalla UI e serve solo per testare lo stile
    "puro Datapizza": un Agent che usa i metodi di SQLDatabase come tools.
    """
    settings = get_settings()

    # URI del database letto dalla configurazione FastAPI (es. SQL Server via pyodbc)
    db_uri = settings.database_url

    # 1. Inizializza il tool SQLDatabase di Datapizza
    db_tool = SQLDatabase(db_uri=db_uri)

    # 2. Client Anthropic con retry (già usato dal resto dell'app)
    client = RetryAnthropicClient(
        api_key=settings.anthropic_api_key,
        model=settings.agent_model,
    )

    # 3. Crea l'agente Datapizza usando i metodi del tool come tools
    system_prompt = (
        "Sei un esperto di database SQL Server. Usa SOLO i tool disponibili per:\n"
        "devi elencarmi solo le tabelle dello schema magazzino."
    )

    agent = Agent(
        name="database_expert_prototype",
        client=client,
        system_prompt=system_prompt,
        tools=[
            db_tool.list_tables,
            db_tool.get_table_schema,
            db_tool.run_sql_query,
        ],
    )

    user_question = "Quanti articoli ci sono in magazzino ok ?"

    print("Domanda utente:", user_question)
    print("\n=== Esecuzione agente Datapizza (SQLDatabase prototype) ===\n")

    result = await agent.a_run(user_question)

    print(result)


if __name__ == "__main__":
    asyncio.run(main())
