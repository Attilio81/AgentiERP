"""
SQL query tools for Datapizza agents.
Tools are created dynamically per agent configuration.
"""
import re
from typing import Any, Dict, List, Optional

from datapizza.tools import tool
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

from app.database.database import engine as default_engine
from app.config import get_settings

settings = get_settings()

_engine_cache: Dict[str, Engine] = {}


def validate_sql_query(query: str) -> tuple[bool, str]:
    """
    Validate SQL query to ensure it's safe.
    Only SELECT statements are allowed, no data modification.
    
    Args:
        query: SQL query string to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Remove comments and normalize whitespace
    query_clean = re.sub(r'--.*$', '', query, flags=re.MULTILINE)
    query_clean = re.sub(r'/\*.*?\*/', '', query_clean, flags=re.DOTALL)
    query_clean = query_clean.strip().upper()
    
    # Check if query starts with SELECT
    if not query_clean.startswith('SELECT'):
        return False, "Solo query SELECT sono permesse. Non puoi modificare i dati."
    
    # Check for dangerous keywords
    dangerous_keywords = [
        'DROP', 'DELETE', 'INSERT', 'UPDATE', 'ALTER', 'CREATE',
        'TRUNCATE', 'REPLACE', 'MERGE', 'EXEC', 'EXECUTE',
        'SP_', 'XP_', 'OPENROWSET', 'OPENDATASOURCE'
    ]
    
    for keyword in dangerous_keywords:
        if keyword in query_clean:
            return False, f"Keyword '{keyword}' non è permessa. Solo query di lettura (SELECT) sono consentite."
    
    return True, ""


def format_results(results: List[Dict[str, Any]], max_rows: int = None) -> str:
    """
    Format query results as a readable string.
    
    Args:
        results: List of row dictionaries
        max_rows: Maximum number of rows to display
        
    Returns:
        Formatted string representation of results
    """
    if not results:
        return "Nessun risultato trovato."
    
    # Limit results if specified
    total_rows = len(results)
    if max_rows:
        results = results[:max_rows]
        truncated = len(results) < total_rows
    else:
        truncated = False
    
    # Get column names
    columns = list(results[0].keys())
    
    # Calculate column widths
    widths = {col: len(str(col)) for col in columns}
    for row in results:
        for col in columns:
            widths[col] = max(widths[col], len(str(row[col])))
    
    # Build formatted string
    lines = []
    
    # Header
    header = " | ".join(str(col).ljust(widths[col]) for col in columns)
    lines.append(header)
    lines.append("-" * len(header))
    
    # Rows
    for row in results:
        line = " | ".join(str(row[col]).ljust(widths[col]) for col in columns)
        lines.append(line)
    
    result = "\n".join(lines)
    
    if truncated:
        result += f"\n\n(Mostrati {len(results)} risultati. Risultati totali potrebbero essere di più su {total_rows} righe totali.)"
    else:
        result += f"\n\n(Totale: {total_rows} righe)"
    
    return result


def _get_engine(db_uri: Optional[str]) -> Engine:
    """Return a SQLAlchemy Engine for the given db_uri.

    If db_uri is None, use the default application engine.
    """

    if not db_uri:
        return default_engine

    if db_uri not in _engine_cache:
        _engine_cache[db_uri] = create_engine(
            db_uri,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
            echo=False,
        )

    return _engine_cache[db_uri]


def execute_query(query: str, db_uri: Optional[str] = None) -> str:
    """Execute a read-only SQL query on the configured database."""

    is_valid, error_msg = validate_sql_query(query)
    if not is_valid:
        return f"ERRORE: {error_msg}"

    engine = _get_engine(db_uri)
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = Session()
    try:
        result = db.execute(
            text(query),
            execution_options={"timeout": settings.query_timeout_seconds},
        )
        rows = result.fetchall()
        results: List[Dict[str, Any]] = [dict(row._mapping) for row in rows]
        return format_results(results, max_rows=settings.max_query_results)
    except Exception as e:
        return f"ERRORE durante l'esecuzione della query: {str(e)}"
    finally:
        db.close()


def create_sql_select_tool(agent_name: str, db_uri: Optional[str]) -> Any:
    """
    Factory che crea un tool SQL SELECT personalizzato per uno specifico agente.

    Questo pattern factory permette di creare tool isolati per ogni agente, ognuno
    con la propria connessione al database configurata.

    Args:
        agent_name: Nome dell'agente (usato per naming del tool)
        db_uri: URI connessione database. Se None, usa il database di default

    Returns:
        Tool function decorato con @tool di Datapizza, pronto per essere usato dall'Agent
    """

    @tool
    def sql_select(query: str) -> str:
        """Esegui una query SQL SELECT di sola lettura sul database configurato per questo agente.

        Usa questo strumento per leggere i dati (mai per modificarli) e POI, nella risposta
        finale all'utente, riassumi sempre cosa mostrano i risultati: andamenti, valori chiave,
        confronti tra periodi, clienti, articoli, ecc.

        Args:
            query: Istruzione SQL che DEVE iniziare con SELECT. Può includere filtri, JOIN,
                   aggregazioni (SUM, AVG, COUNT, ecc.), GROUP BY e ORDER BY, ma non comandi
                   di modifica dei dati (INSERT, UPDATE, DELETE, ecc.).

        Returns:
            Una tabella di testo leggibile con i risultati della query oppure un messaggio
            di errore se la query non è valida o non può essere eseguita.
        """

        return execute_query(query, db_uri=db_uri)

    # Renaming dinamico del tool per facilitare il debug e il logging
    sql_select.__name__ = f"{agent_name}_sql_select"
    return sql_select


def create_get_schema_tool(agent_name: str, db_uri: Optional[str], schema_name: Optional[str] = None) -> Any:
    """
    Factory che crea un tool per esplorare lo schema del database.

    Questo tool permette agli agenti di scoprire autonomamente quali tabelle e colonne
    sono disponibili, rendendo le risposte più accurate senza dover hardcodare
    lo schema nel system prompt.

    Args:
        agent_name: Nome dell'agente (usato per naming del tool)
        db_uri: URI connessione database. Se None, usa il database di default
        schema_name: Nome dello schema SQL da esplorare (es. 'dbo', 'magazzino').
                    Se None, esplora tutti gli schemi.

    Returns:
        Tool function che restituisce informazioni su tabelle e colonne

    Example:
        >>> tool = create_get_schema_tool("vendite", None, "dbo")
        >>> result = tool("Clienti")
        # Restituisce: struttura della tabella Clienti con nomi colonne e tipi
    """

    @tool
    def get_schema(table_name: str = "") -> str:
        """Ottieni informazioni sullo schema del database (tabelle, colonne, tipi di dati).

        Questo strumento è fondamentale per capire quali dati sono disponibili prima
        di scrivere una query SQL. Usalo SEMPRE quando non sei sicuro di quali
        tabelle/colonne esistano.

        Args:
            table_name: Nome specifico di una tabella da ispezionare (opzionale).
                       Se vuoto, restituisce tutte le tabelle disponibili.
                       Esempi: "Clienti", "Ordini", "Prodotti"

        Returns:
            Informazioni strutturate su:
            - Nomi delle tabelle disponibili (se table_name è vuoto)
            - Colonne, tipi di dati, nullable per la tabella specifica (se table_name fornito)

        Examples:
            get_schema("")  # Lista tutte le tabelle
            get_schema("Clienti")  # Mostra struttura tabella Clienti
        """

        # Query per ottenere informazioni sullo schema da INFORMATION_SCHEMA
        # (standard SQL supportato da SQL Server)
        if table_name.strip():
            # Caso 1: Dettagli di una tabella specifica
            query = """
            SELECT
                TABLE_SCHEMA,
                TABLE_NAME,
                COLUMN_NAME,
                DATA_TYPE,
                CHARACTER_MAXIMUM_LENGTH,
                IS_NULLABLE,
                COLUMN_DEFAULT
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = :table_name
            """

            # Filtra per schema se specificato
            if schema_name:
                query += " AND TABLE_SCHEMA = :schema_name"

            query += " ORDER BY ORDINAL_POSITION"

            # Esegui query parametrizzata (protezione SQL injection)
            engine = _get_engine(db_uri)
            Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
            db = Session()

            try:
                params = {"table_name": table_name.strip()}
                if schema_name:
                    params["schema_name"] = schema_name

                result = db.execute(
                    text(query),
                    params,
                    execution_options={"timeout": settings.query_timeout_seconds}
                )
                rows = result.fetchall()

                if not rows:
                    return f"TABELLA NON TROVATA: '{table_name}'. Usa get_schema() senza parametri per vedere tutte le tabelle."

                results: List[Dict[str, Any]] = [dict(row._mapping) for row in rows]
                return format_results(results, max_rows=100)

            except Exception as e:
                return f"ERRORE durante il recupero dello schema: {str(e)}"
            finally:
                db.close()

        else:
            # Caso 2: Lista di tutte le tabelle disponibili
            query = """
            SELECT DISTINCT
                TABLE_SCHEMA,
                TABLE_NAME,
                TABLE_TYPE
            FROM INFORMATION_SCHEMA.TABLES
            WHERE TABLE_TYPE = 'BASE TABLE' OR TABLE_TYPE = 'VIEW'
            """

            # Filtra per schema se specificato
            if schema_name:
                query += " AND TABLE_SCHEMA = :schema_name"

            query += " ORDER BY TABLE_SCHEMA, TABLE_NAME"

            engine = _get_engine(db_uri)
            Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
            db = Session()

            try:
                params = {"schema_name": schema_name} if schema_name else {}
                result = db.execute(
                    text(query),
                    params,
                    execution_options={"timeout": settings.query_timeout_seconds}
                )
                rows = result.fetchall()
                results: List[Dict[str, Any]] = [dict(row._mapping) for row in rows]

                if not results:
                    return "Nessuna tabella trovata nello schema specificato."

                return format_results(results, max_rows=100)

            except Exception as e:
                return f"ERRORE durante il recupero della lista tabelle: {str(e)}"
            finally:
                db.close()

    # Renaming dinamico per debug
    get_schema.__name__ = f"{agent_name}_get_schema"
    return get_schema
