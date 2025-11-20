"""
Application configuration using Pydantic Settings.
Environment variables are loaded from .env file.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database Configuration
    database_url: str
    
    # Anthropic API Configuration
    anthropic_api_key: str
    agent_model: str = "claude-sonnet-4-5-20250929"
    faq_model: str | None = None
    
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
