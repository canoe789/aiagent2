"""
Pydantic models for Project HELIX v2.0 database entities
"""

from datetime import datetime
from enum import Enum
from typing import Optional, Any, Dict
from pydantic import BaseModel, Field, ConfigDict


class JobStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class TaskStatus(str, Enum):
    PENDING = "PENDING"
    ASSIGNED = "ASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    RETRYING = "RETRYING"
    ORCHESTRATED = "ORCHESTRATED"  # Task processed by orchestrator


class JobCreate(BaseModel):
    """Request model for creating a new job"""
    chat_input: str = Field(..., min_length=10, description="User's creative requirement")
    session_id: Optional[str] = Field(None, description="Optional session identifier")


class Job(BaseModel):
    """Job database model"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    status: JobStatus
    initial_request: Dict[str, Any]
    session_id: Optional[str]
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
    error_message: Optional[str]


class TaskCreate(BaseModel):
    """Request model for creating a new task"""
    job_id: int
    agent_id: str = Field(..., max_length=50)
    input_data: Dict[str, Any] = Field(default_factory=dict)


class Task(BaseModel):
    """Task database model"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    job_id: int
    agent_id: str
    status: TaskStatus
    input_data: Dict[str, Any]
    output_data: Optional[Dict[str, Any]]
    error_log: Optional[str]
    retry_count: int
    assigned_at: Optional[datetime]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime


class AgentPrompt(BaseModel):
    """Agent prompt database model"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    agent_id: str
    version: str
    prompt_text: str
    is_active: bool
    created_at: datetime
    created_by: str


class Artifact(BaseModel):
    """Artifact database model"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    task_id: int
    name: str
    schema_id: str
    payload: Dict[str, Any]
    created_at: datetime


class SystemLog(BaseModel):
    """System log database model"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    level: str
    component: str
    message: str
    metadata: Dict[str, Any]
    created_at: datetime


# Input/Output Protocol Models
class ArtifactReference(BaseModel):
    """Reference to an artifact produced by another task"""
    name: str = Field(..., description="Artifact name to reference")
    source_task_id: int = Field(..., description="Task ID that produced this artifact")


class TaskInput(BaseModel):
    """Standard task input format"""
    artifacts: list[ArtifactReference] = Field(default_factory=list)
    params: Dict[str, Any] = Field(default_factory=dict)


class TaskOutput(BaseModel):
    """Standard task output format"""
    schema_id: str = Field(..., description="Schema identifier for validation")
    payload: Dict[str, Any] = Field(..., description="Actual output data")


# API Response Models
class JobResponse(BaseModel):
    """API response for job operations"""
    job_id: int
    status: JobStatus
    message: str
    created_at: datetime
    error_message: Optional[str] = None
    tasks: Optional[list] = None


class TaskResponse(BaseModel):
    """API response for task operations"""
    task_id: int
    status: TaskStatus
    agent_id: str
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_log: Optional[str] = None