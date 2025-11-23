"""
Client wrapper per Anthropic con retry logic e I/O tracing.

Questo modulo estende AnthropicClient con:
1. Retry automatico per errori 529 Overloaded (backoff esponenziale)
2. I/O tracing per debugging (logging completo di input/output LLM)
3. Metriche di performance (latenza, token usage)

Usage:
    client = RetryAnthropicClient(
        api_key="sk-ant-...",
        trace_io=True  # Abilita logging dettagliato
    )
"""
from typing import Any, AsyncIterator, Dict, Iterator, List, Optional, Union
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from datapizza.clients.anthropic import AnthropicClient
import anthropic
import json
import time
from datetime import datetime


class RetryAnthropicClient(AnthropicClient):
    """
    Wrapper attorno ad AnthropicClient che aggiunge:
    - Retry logic per errori 529 Overloaded (Anthropic sovraccarico)
    - I/O tracing opzionale per debugging (input/output LLM completi)
    - Performance metrics (latenza, token usage)

    Args:
        api_key: Chiave API Anthropic
        trace_io: Se True, logga tutti gli input/output delle chiamate LLM
        model: Modello di default da usare (es. 'claude-sonnet-4-5-20250929')
        **kwargs: Altri parametri passati ad AnthropicClient

    Example:
        >>> client = RetryAnthropicClient(
        ...     api_key="sk-ant-xxx",
        ...     trace_io=True  # Debugging mode
        ... )
        >>> response = client.invoke("Hello, Claude!")
        [2025-11-23 10:30:45] [I/O TRACE] INPUT: "Hello, Claude!"
        [2025-11-23 10:30:46] [I/O TRACE] OUTPUT: "Hello! How can I help you?"
    """

    def __init__(self, *args, trace_io: bool = False, **kwargs):
        """
        Inizializza il client con opzioni retry e tracing.

        Args:
            trace_io: Abilita logging dettagliato I/O (default: False)
                     ATTENZIONE: in produzione può generare log molto grandi
        """
        super().__init__(*args, **kwargs)
        self.trace_io = trace_io  # Flag per abilitare/disabilitare I/O tracing

    def _log_io(self, direction: str, data: Any, duration_ms: float = None):
        """
        Logga input/output delle chiamate LLM per debugging.

        Args:
            direction: 'INPUT' o 'OUTPUT'
            data: Dati da loggare (dict, str, ecc.)
            duration_ms: Latenza in millisecondi (opzionale, solo per OUTPUT)
        """
        if not self.trace_io:
            return  # Tracing disabilitato

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

        # Formatta i dati in modo leggibile
        if isinstance(data, dict):
            # Troncamento smart per dizionari grandi
            data_str = json.dumps(data, indent=2, ensure_ascii=False)
            if len(data_str) > 2000:
                data_str = data_str[:2000] + f"\n... [troncato, {len(data_str)} caratteri totali]"
        elif isinstance(data, str):
            if len(data) > 1000:
                data_str = data[:1000] + f"\n... [troncato, {len(data)} caratteri totali]"
            else:
                data_str = data
        else:
            data_str = str(data)

        # Log formattato
        print(f"\n{'='*80}")
        print(f"[{timestamp}] [I/O TRACE] {direction}")
        if duration_ms is not None:
            print(f"[LATENCY] {duration_ms:.2f}ms")
        print(f"{'-'*80}")
        print(data_str)
        print(f"{'='*80}\n")

    def _is_overloaded_error(exception):
        """
        Verifica se l'eccezione è un errore 529 Overloaded di Anthropic.

        Gli errori 529 indicano che il server è sovraccarico e la richiesta
        dovrebbe essere ritentata dopo un delay.
        """
        return (
            isinstance(exception, anthropic.APIStatusError) and
            exception.status_code == 529
        )

    def _should_retry(retry_state):
        """
        Predicato custom per tenacity: determina se ritentare la chiamata.

        Ritenta SOLO su errori 529 Overloaded, non su altri errori API
        (es. 400 Bad Request, 401 Unauthorized, ecc.)
        """
        exception = retry_state.outcome.exception()
        return (
            isinstance(exception, anthropic.APIStatusError) and
            exception.status_code == 529
        )

    @retry(
        wait=wait_exponential(multiplier=1, min=1, max=60),
        stop=stop_after_attempt(5),
        retry=_should_retry
    )
    def invoke(self, *args, **kwargs) -> str:
        """
        Invoca il modello LLM in modalità sincrona con retry e tracing.

        Questa versione wrappa super().invoke() aggiungendo:
        - Retry automatico su errori 529 (max 5 tentativi)
        - I/O tracing se abilitato (log input/output/latenza)

        Returns:
            Risposta testuale del modello
        """
        # Log INPUT se tracing abilitato
        if self.trace_io:
            self._log_io("INPUT", {
                "args": args,
                "kwargs": {k: v for k, v in kwargs.items() if k != "api_key"}  # No API key in logs
            })

        # Esegui chiamata con timing
        start_time = time.time()
        result = super().invoke(*args, **kwargs)
        duration_ms = (time.time() - start_time) * 1000

        # Log OUTPUT se tracing abilitato
        if self.trace_io:
            self._log_io("OUTPUT", result, duration_ms=duration_ms)

        return result

    @retry(
        wait=wait_exponential(multiplier=1, min=1, max=60),
        stop=stop_after_attempt(5),
        retry=_should_retry
    )
    def stream_invoke(self, *args, **kwargs) -> Iterator[str]:
        """
        Invoca il modello in streaming mode (sync) con retry.

        NOTA: I/O tracing disabilitato per streaming (troppo verboso)
        """
        # Log INPUT se tracing abilitato
        if self.trace_io:
            self._log_io("INPUT (STREAM)", {
                "args": args,
                "kwargs": {k: v for k, v in kwargs.items() if k != "api_key"}
            })

        return super().stream_invoke(*args, **kwargs)

    @retry(
        wait=wait_exponential(multiplier=1, min=1, max=60),
        stop=stop_after_attempt(5),
        retry=_should_retry
    )
    async def a_invoke(self, *args, **kwargs) -> str:
        """
        Invoca il modello LLM in modalità asincrona con retry e tracing.

        Questa è la versione async di invoke(), usata da Datapizza Agent.

        Returns:
            Risposta testuale del modello
        """
        # Log INPUT se tracing abilitato
        if self.trace_io:
            self._log_io("INPUT (ASYNC)", {
                "args": args,
                "kwargs": {k: v for k, v in kwargs.items() if k != "api_key"}
            })

        # Esegui chiamata con timing
        start_time = time.time()
        result = await super().a_invoke(*args, **kwargs)
        duration_ms = (time.time() - start_time) * 1000

        # Log OUTPUT se tracing abilitato
        if self.trace_io:
            self._log_io("OUTPUT (ASYNC)", result, duration_ms=duration_ms)

        return result

    @retry(
        wait=wait_exponential(multiplier=1, min=1, max=60),
        stop=stop_after_attempt(5),
        retry=_should_retry
    )
    def a_stream_invoke(self, *args, **kwargs) -> AsyncIterator[str]:
        """
        Invoca il modello in streaming mode (async) con retry.

        NOTA IMPORTANTE:
        - Retry funziona solo sulla *creazione* del generatore, non sull'iterazione
        - Gli errori 529 normalmente avvengono all'inizio della richiesta
        - I/O tracing disabilitato per streaming (troppo verboso)
        """
        # Log INPUT se tracing abilitato
        if self.trace_io:
            self._log_io("INPUT (ASYNC STREAM)", {
                "args": args,
                "kwargs": {k: v for k, v in kwargs.items() if k != "api_key"}
            })

        return super().a_stream_invoke(*args, **kwargs)
