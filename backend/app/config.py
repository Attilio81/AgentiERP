"""
Application configuration using Pydantic Settings.
Environment variables are loaded from .env file.
"""
from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database Configuration
    database_url: str
    
    # LLM Provider Configuration
    llm_provider: Literal["anthropic", "openai", "gemini"] = "anthropic"

    # Anthropic API Configuration
    anthropic_api_key: str | None = None

    # OpenAI API Configuration
    openai_api_key: str | None = None

    # Google Gemini API Configuration
    gemini_api_key: str | None = None

    # Model configuration (heavy vs light)
    agent_model: str | None = "claude-3-5-sonnet-20241022"
    faq_model: str | None = "claude-3-5-haiku-20241022"
    
    # Security Configuration
    secret_key: str
    session_expire_hours: int = 24
    
    # API Configuration
    backend_url: str = "http://localhost:8000"
    frontend_url: str = "http://localhost:8501"
    
    # SQL Query Limits
    max_query_results: int = 100
    query_timeout_seconds: int = 30
    
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
