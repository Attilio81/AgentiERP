"""
Application configuration using Pydantic Settings.
Environment variables are loaded from .env file.

Tutte le configurazioni possono essere sovrascritte tramite variabili d'ambiente.
Esempio: export DATABASE_URL="mssql+pyodbc://..."
"""
from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Configurazione applicazione caricata da variabili d'ambiente.

    Le variabili vengono lette dal file .env (se presente) o dall'ambiente.
    """

    # ========================================
    # DATABASE CONFIGURATION
    # ========================================
    database_url: str  # Obbligatorio: connection string SQL Server

    # ========================================
    # LLM PROVIDER CONFIGURATION
    # ========================================
    llm_provider: Literal["anthropic", "openai", "gemini"] = "anthropic"

    # Anthropic API Configuration
    anthropic_api_key: str | None = None

    # OpenAI API Configuration
    openai_api_key: str | None = None

    # Google Gemini API Configuration
    gemini_api_key: str | None = None

    # ========================================
    # MODEL CONFIGURATION
    # ========================================
    # Model configuration (heavy vs light)
    agent_model: str | None = "claude-3-5-sonnet-20241022"  # Modello per agenti (analisi complesse)
    faq_model: str | None = "claude-3-5-haiku-20241022"    # Modello per FAQ (più economico)

    # ========================================
    # DEBUGGING & OBSERVABILITY
    # ========================================
    enable_llm_tracing: bool = False  # Se True, logga tutti gli input/output LLM
                                      # ATTENZIONE: genera log molto grandi!
                                      # Utile per debugging ma disabilitare in produzione

    # ========================================
    # SECURITY CONFIGURATION
    # ========================================
    secret_key: str  # Obbligatorio: chiave segreta per JWT (generare con secrets.token_urlsafe(32))
    session_expire_hours: int = 24  # Durata sessioni utente

    # ========================================
    # API CONFIGURATION
    # ========================================
    backend_url: str = "http://localhost:8000"
    frontend_url: str = "http://localhost:8501"

    # ========================================
    # SQL QUERY LIMITS
    # ========================================
    max_query_results: int = 100  # Numero massimo righe restituite da query SQL
    query_timeout_seconds: int = 30  # Timeout query SQL
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Uses lru_cache to avoid reading .env file multiple times.
    """
    return Settings()
