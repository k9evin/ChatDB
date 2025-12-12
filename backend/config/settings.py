"""Configuration management using Pydantic Settings."""

from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # OpenRouter Configuration
    openrouter_api_key: str
    openrouter_model: str = "openai/gpt-4o-mini"
    openrouter_base_url: str = "https://openrouter.ai/api/v1"

    # Embedding Configuration
    embedding_model: str = "text-embedding-3-small"
    embedding_provider: str = "openai"  # or "openrouter"

    # Database Configuration
    database_url: str = "sqlite:///./demo_database.db"

    # LangSmith (optional)
    langchain_tracing_v2: bool = False
    langchain_api_key: Optional[str] = None
    langchain_project: str = "ChatDB-Agent"

    # Agent Configuration
    max_retries: int = 3
    max_context_length: int = 128000
    temperature: float = 0.0
    # Keep this reasonably low; we also add a loop-guard in the graph to avoid hangs.
    recursion_limit: int = 25  # Maximum number of graph steps to prevent infinite loops

    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_debug: bool = True
    cors_origins: str = "*"  # Comma-separated list or "*" for all

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
