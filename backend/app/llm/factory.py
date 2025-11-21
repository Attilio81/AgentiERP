"""Utility functions for instantiating LLM clients based on configuration."""
from __future__ import annotations

from typing import Literal, Optional

from app.agents.client_wrapper import RetryAnthropicClient
from app.config import Settings


class LLMConfigurationError(RuntimeError):
    """Raised when an LLM client cannot be initialized due to configuration issues."""


UseCase = Literal["agent", "faq"]


def _resolve_model(settings: Settings, use_case: UseCase, override: Optional[str]) -> str:
    """Return the model to use for the given use case."""
    if override:
        return override

    if use_case == "agent":
        if settings.agent_model:
            return settings.agent_model
    else:
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
    """Instantiate the correct Datapizza client for the configured provider."""
    provider = (settings.llm_provider or "anthropic").lower()
    model_name = _resolve_model(settings, use_case, model_override)

    if provider == "anthropic":
        if not settings.anthropic_api_key:
            raise LLMConfigurationError(
                "Configura ANTHROPIC_API_KEY per utilizzare il provider Anthropic."
            )
        return RetryAnthropicClient(
            api_key=settings.anthropic_api_key,
            model=model_name,
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
