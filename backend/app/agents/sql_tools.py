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
    """Factory for a generic SELECT tool bound to an agent."""

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

    sql_select.__name__ = f"{agent_name}_sql_select"
    return sql_select
