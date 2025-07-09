"""
Configuration module for Project HELIX v2.0
Centralizes all configuration settings including paths
"""

import os
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field


class PathConfig(BaseModel):
    """Path configuration for the project"""
    # Get project root directory (2 levels up from src/config.py)
    project_root: Path = Field(
        default_factory=lambda: Path(__file__).parent.parent.resolve()
    )
    
    @property
    def schemas_dir(self) -> Path:
        """Get schemas directory path"""
        return self.project_root / "schemas"
    
    @property
    def prompts_dir(self) -> Path:
        """Get prompts directory path (if exists)"""
        return self.project_root / "prompts"
    
    @property
    def logs_dir(self) -> Path:
        """Get logs directory path"""
        return self.project_root / "logs"
    
    def get_schema_path(self, schema_id: str) -> Path:
        """
        Get full path to a schema file
        
        Args:
            schema_id: Schema identifier (e.g., "CreativeBrief_v1.0")
            
        Returns:
            Path to the schema JSON file
        """
        return self.schemas_dir / f"{schema_id}.json"


class DatabaseConfig(BaseModel):
    """Database configuration"""
    url: str = Field(
        default_factory=lambda: os.getenv(
            "DATABASE_URL", 
            "postgresql://helix:helix123@localhost:5432/helix_db"
        )
    )
    pool_min_size: int = Field(default=5)
    pool_max_size: int = Field(default=20)
    command_timeout: int = Field(default=60)


class AgentConfig(BaseModel):
    """Agent-specific configuration"""
    max_retry_count: int = Field(default=3)
    retry_delay_seconds: int = Field(default=5)
    task_timeout_seconds: int = Field(default=300)  # 5 minutes
    enable_performance_metrics: bool = Field(default=True)


class Config(BaseModel):
    """Main configuration class"""
    paths: PathConfig = Field(default_factory=PathConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    agent: AgentConfig = Field(default_factory=AgentConfig)
    
    # Environment
    environment: str = Field(
        default_factory=lambda: os.getenv("ENVIRONMENT", "development")
    )
    debug: bool = Field(
        default_factory=lambda: os.getenv("DEBUG", "false").lower() == "true"
    )


# Global configuration instance
config = Config()


# Helper functions for backward compatibility
def get_project_root() -> Path:
    """Get project root directory"""
    return config.paths.project_root


def get_schema_path(schema_id: str) -> Path:
    """Get full path to a schema file"""
    return config.paths.get_schema_path(schema_id)