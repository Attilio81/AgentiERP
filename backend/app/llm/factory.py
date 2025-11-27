"""
Utility functions for instantiating LLM clients based on configuration.

Questo modulo fornisce una factory per creare client LLM multi-provider:
- Anthropic (Claude) - con retry logic e tracing
- OpenAI (GPT)
- Google (Gemini)

Il provider viene selezionato tramite la variabile LLM_PROVIDER in .env
"""
from __future__ import annotations

from typing import Literal, Optional

from app.agents.client_wrapper import RetryAnthropicClient
from app.config import Settings


class LLMConfigurationError(RuntimeError):
    """
    Eccezione sollevata quando un client LLM non può essere inizializzato.

    Cause comuni:
    - API key mancante (ANTHROPIC_API_KEY, OPENAI_API_KEY, GEMINI_API_KEY)
    - Modello non configurato (AGENT_MODEL, FAQ_MODEL)
    - Provider non supportato
    - Dipendenze mancanti (es. datapizza-ai-clients-openai)
    """


UseCase = Literal["agent", "faq"]


def _resolve_model(settings: Settings, use_case: UseCase, override: Optional[str]) -> str:
    """
    Risolve quale modello LLM usare in base al use case.

    Logica di risoluzione:
    1. Se model_override fornito → usa quello
    2. Se use_case == "agent" → usa AGENT_MODEL (modello pesante)
    3. Se use_case == "faq" → usa FAQ_MODEL (modello leggero) o fallback a AGENT_MODEL
    4. Altrimenti → solleva errore

    Args:
        settings: Configurazione applicazione
        use_case: Tipo di utilizzo ("agent" per analisi, "faq" per suggerimenti)
        override: Modello specifico da forzare (opzionale)

    Returns:
        Nome del modello da usare (es. "claude-sonnet-4-5-20250929")

    Raises:
        LLMConfigurationError: Se nessun modello è configurato
    """
    if override:
        return override

    if use_case == "agent":
        if settings.agent_model:
            return settings.agent_model
    else:
        # FAQ: preferisci modello leggero, altrimenti fallback a AGENT_MODEL
        if settings.faq_model:
            return settings.faq_model
        if settings.agent_model:
            return settings.agent_model

    raise LLMConfigurationError(
        "Nessun modello configurato per l'LLM. Imposta AGENT_MODEL o FAQ_MODEL."  # noqa: E501
    )


def build_llm_client(
    settings: Settings,
    *,
    use_case: UseCase,
    model_override: Optional[str] = None,
):
    """
    Factory per creare il client LLM corretto in base al provider configurato.

    Questa factory:
    1. Legge il provider da settings.llm_provider (default: "anthropic")
    2. Risolve il modello da usare (AGENT_MODEL vs FAQ_MODEL)
    3. Valida che l'API key sia presente
    4. Crea il client con retry logic e tracing (se abilitato)

    Args:
        settings: Configurazione applicazione
        use_case: "agent" (analisi) o "faq" (suggerimenti)
        model_override: Modello specifico da forzare (opzionale)

    Returns:
        Client Datapizza configurato (AnthropicClient, OpenAIClient, GoogleClient)

    Raises:
        LLMConfigurationError: Se configurazione mancante o provider non supportato

    Example:
        >>> settings = get_settings()
        >>> client = build_llm_client(settings, use_case="agent")
        >>> response = client.invoke("Analizza le vendite 2025")
    """
    provider = (settings.llm_provider or "anthropic").lower()
    model_name = _resolve_model(settings, use_case, model_override)

    # ========================================
    # ANTHROPIC (CLAUDE)
    # ========================================
    if provider == "anthropic":
        if not settings.anthropic_api_key:
            raise LLMConfigurationError(
                "Configura ANTHROPIC_API_KEY per utilizzare il provider Anthropic."
            )

        # Crea client con retry logic e I/O tracing opzionale
        return RetryAnthropicClient(
            api_key=settings.anthropic_api_key,
            model=model_name,
            temperature=settings.llm_temperature,  # Temperatura configurabile da .env
            trace_io=settings.enable_llm_tracing,  # NUOVO: I/O tracing configurabile
        )

    if provider == "openai":
        try:
            from datapizza.clients.openai import OpenAIClient  # type: ignore
        except ImportError as exc:  # pragma: no cover - informative error
            raise LLMConfigurationError(
                "Client OpenAI non disponibile. Installa 'datapizza-ai-clients-openai'."
            ) from exc

        if not settings.openai_api_key:
            raise LLMConfigurationError(
                "Configura OPENAI_API_KEY per utilizzare il provider OpenAI."
            )

        return OpenAIClient(
            api_key=settings.openai_api_key,
            model=model_name,
        )

    if provider == "gemini":
        try:
            from datapizza.clients.google import GoogleClient  # type: ignore
        except ImportError as exc:  # pragma: no cover - informative error
            raise LLMConfigurationError(
                "Client Gemini non disponibile. Installa 'datapizza-ai-clients-google'."
            ) from exc

        if not settings.gemini_api_key:
            raise LLMConfigurationError(
                "Configura GEMINI_API_KEY per utilizzare il provider Gemini."
            )

        return GoogleClient(
            api_key=settings.gemini_api_key,
            model=model_name,
        )

    raise LLMConfigurationError(
        f"Provider LLM '{provider}' non supportato. Usa anthropic, openai o gemini."
    )
