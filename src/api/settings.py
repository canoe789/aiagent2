"""
Application settings for Project HELIX v2.0
"""

from pydantic_settings import BaseSettings
from pydantic import ConfigDict, field_validator
from typing import Optional, Union


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
    debug: bool = False
    
    # Orchestrator settings
    orchestrator_poll_interval: int = 5
    max_retry_attempts: int = 3
    orchestrator_port: Optional[int] = None
    worker_port: Optional[int] = None
    
    @field_validator('orchestrator_port', 'worker_port', mode='before')
    @classmethod
    def parse_optional_int_port(cls, v):
        """Convert empty string to None for optional port fields"""
        if v == '' or v is None:
            return None
        return int(v)
    
    # Security settings
    secret_key: str = "dev_secret_key_change_in_production"
    cors_origins: str = "http://localhost:*,https://localhost:*"
    
    # Performance settings
    db_pool_min_size: int = 5
    db_pool_max_size: int = 20
    api_timeout: int = 30
    agent_timeout: int = 300
    
    # Development settings
    auto_reload: bool = True
    enable_docs: bool = True
    verbose_logging: bool = False
    
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"  # 忽略额外字段
    )


# Global settings instance
settings = Settings()