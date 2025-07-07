"""
Application settings for Project HELIX v2.0
"""

from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application configuration settings"""
    
    # Database settings
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "helix"
    postgres_user: str = "helix_user"
    postgres_password: str = "helix_password"
    
    # API settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # AI Model API keys
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    deepseek_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    
    # AI Model settings
    default_ai_provider: str = "deepseek"
    default_temperature: float = 0.7
    default_max_tokens: int = 4000
    
    # Application settings
    environment: str = "development"
    log_level: str = "INFO"
    
    # Orchestrator settings
    orchestrator_poll_interval: int = 5
    max_retry_attempts: int = 3
    
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )


# Global settings instance
settings = Settings()