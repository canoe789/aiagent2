"""
Agent SDK for Project HELIX v2.0
Provides core functionality for agent development
"""

import asyncio
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
import structlog
from datetime import datetime
import json
import jsonschema
import os

from database.connection import db_manager
from database.models import (
    Task, TaskStatus, TaskInput, TaskOutput, 
    Artifact, AgentPrompt
)

logger = structlog.get_logger(__name__)


class BaseAgent(ABC):
    """
    Base class for all HELIX agents
    Provides standard lifecycle and data access methods
    """
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.current_task: Optional[Task] = None
        
    @abstractmethod
    async def process_task(self, task_input: TaskInput) -> TaskOutput:
        """
        Main task processing method - must be implemented by each agent
        
        Args:
            task_input: Standard task input with artifacts and params
            
        Returns:
            TaskOutput: Standard task output with schema_id and payload
        """
        pass
    
    async def run_task(self, task_id: int) -> bool:
        """
        Execute a specific task from the database
        
        Args:
            task_id: The task ID to process
            
        Returns:
            bool: True if task completed successfully, False otherwise
        """
        try:
            # Get task from database
            task = await self.get_task(task_id)
            if not task:
                logger.error("Task not found", task_id=task_id)
                return False
            
            self.current_task = task
            
            # Mark task as in progress
            await self.update_task_status(task_id, TaskStatus.IN_PROGRESS)
            
            logger.info("Starting task processing", 
                       task_id=task_id, agent_id=self.agent_id)
            
            # Parse task input
            task_input = TaskInput.model_validate(task.input_data)
            
            # Process the task
            task_output = await self.process_task(task_input)
            
            # Save the output
            await self.save_task_output(task_id, task_output)
            
            # Mark task as completed
            await self.update_task_status(task_id, TaskStatus.COMPLETED)
            
            logger.info("Task completed successfully", 
                       task_id=task_id, agent_id=self.agent_id)
            
            return True
            
        except Exception as e:
            logger.error("Task processing failed", 
                        task_id=task_id, agent_id=self.agent_id, error=str(e))
            
            # Mark task as failed and log error
            await self.update_task_status(task_id, TaskStatus.FAILED, str(e))
            return False
    
    async def get_task(self, task_id: int) -> Optional[Task]:
        """Get task details from database"""
        query = "SELECT * FROM tasks WHERE id = $1"
        result = await db_manager.fetch_one(query, task_id)
        return Task.model_validate(result) if result else None
    
    async def update_task_status(self, task_id: int, status: TaskStatus, error_log: Optional[str] = None):
        """Update task status in database"""
        if status == TaskStatus.IN_PROGRESS:
            query = """
                UPDATE tasks 
                SET status = $1, started_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
                WHERE id = $2
            """
            await db_manager.execute(query, status, task_id)
        elif status == TaskStatus.COMPLETED:
            query = """
                UPDATE tasks 
                SET status = $1, completed_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
                WHERE id = $2
            """
            await db_manager.execute(query, status, task_id)
        elif status == TaskStatus.FAILED:
            query = """
                UPDATE tasks 
                SET status = $1, error_log = $2, updated_at = CURRENT_TIMESTAMP
                WHERE id = $3
            """
            await db_manager.execute(query, status, error_log, task_id)
    
    async def save_task_output(self, task_id: int, output: TaskOutput):
        """Save task output to database with schema validation"""
        try:
            # Validate output against schema before saving
            import jsonschema
            import os
            
            # Load the schema file
            schema_path = os.path.join(os.path.dirname(__file__), "..", "schemas", f"{output.schema_id}.json")
            if not os.path.exists(schema_path):
                raise ValueError(f"Schema file not found for schema_id: {output.schema_id}")
            
            with open(schema_path, 'r') as f:
                schema = json.load(f)
            
            # Validate the payload against the schema
            jsonschema.validate(instance=output.payload, schema=schema)
            logger.info("Output payload validated successfully against schema", 
                       task_id=task_id, schema_id=output.schema_id)
            
            # Save the validated output
            query = """
                UPDATE tasks 
                SET output_data = $1, updated_at = CURRENT_TIMESTAMP
                WHERE id = $2
            """
            await db_manager.execute(query, output.model_dump(), task_id)
        except jsonschema.ValidationError as ve:
            logger.error("Schema validation failed for task output", 
                         task_id=task_id, schema_id=output.schema_id, error=str(ve))
            raise ValueError(f"Output schema validation failed: {str(ve)}") from ve
        except Exception as e:
            logger.error("Failed to save task output or validate schema", 
                         task_id=task_id, error=str(e))
            raise
    
    async def get_artifacts(self, artifact_refs: List[Any]) -> Dict[str, Any]:
        """
        Batch fetch artifacts referenced in task input
        
        Args:
            artifact_refs: List of artifact references with name and source_task_id
            
        Returns:
            Dict mapping artifact names to their payload data
        """
        artifacts = {}
        
        if not artifact_refs:
            return artifacts
        
        # Build batch query for all artifacts
        # Handle both dict and ArtifactReference objects
        task_ids = []
        names = []
        
        for ref in artifact_refs:
            if hasattr(ref, 'source_task_id'):  # ArtifactReference object
                task_ids.append(ref.source_task_id)
                names.append(ref.name)
            else:  # Dict object
                task_ids.append(ref["source_task_id"])
                names.append(ref["name"])
        
        query = """
            SELECT a.name, a.payload, a.schema_id
            FROM artifacts a
            JOIN tasks t ON a.task_id = t.id
            WHERE t.id = ANY($1) AND a.name = ANY($2)
        """
        
        results = await db_manager.fetch_all(query, task_ids, names)
        
        for result in results:
            # Handle JSON string payloads from database
            payload = result["payload"]
            if isinstance(payload, str):
                import json
                payload = json.loads(payload)
            
            artifacts[result["name"]] = {
                "payload": payload,
                "schema_id": result["schema_id"]
            }
        
        logger.info("Fetched artifacts", 
                   agent_id=self.agent_id, 
                   artifact_count=len(artifacts))
        
        return artifacts
    
    async def get_agent_prompt(self, version: Optional[str] = None) -> Optional[str]:
        """
        Get the agent's prompt from database
        
        Args:
            version: Specific version to get, or latest active if None
            
        Returns:
            str: The prompt text, or None if not found
        """
        if version:
            query = """
                SELECT prompt_text FROM agent_prompts 
                WHERE agent_id = $1 AND version = $2
            """
            result = await db_manager.fetch_one(query, self.agent_id, version)
        else:
            query = """
                SELECT prompt_text FROM agent_prompts 
                WHERE agent_id = $1 AND is_active = true
                ORDER BY created_at DESC
                LIMIT 1
            """
            result = await db_manager.fetch_one(query, self.agent_id)
        
        return result["prompt_text"] if result else None
    
    async def log_system_event(self, level: str, message: str, metadata: Optional[Dict] = None):
        """Log a system event"""
        import json
        
        query = """
            INSERT INTO system_logs (level, component, message, metadata)
            VALUES ($1, $2, $3, $4::jsonb)
        """
        
        metadata_json = json.dumps(metadata or {})
        
        await db_manager.execute(
            query, 
            level, 
            f"agent_{self.agent_id}", 
            message, 
            metadata_json
        )


class AgentWorker:
    """
    Worker that polls for tasks assigned to specific agents
    Can run multiple agent types in one worker process
    """
    
    def __init__(self, agent_classes: Dict[str, BaseAgent]):
        """
        Initialize worker with agent classes
        
        Args:
            agent_classes: Dict mapping agent_id to agent instance
        """
        self.agents = agent_classes
        self.running = False
        self.poll_interval = 5  # seconds
        
    async def start(self):
        """Start the worker polling loop"""
        logger.info("Starting agent worker", agents=list(self.agents.keys()))
        
        await db_manager.connect()
        self.running = True
        
        # Start polling loop
        await self._poll_tasks()
    
    async def stop(self):
        """Stop the worker"""
        logger.info("Stopping agent worker")
        self.running = False
        await db_manager.disconnect()
    
    async def _poll_tasks(self):
        """Poll for pending tasks assigned to our agents"""
        while self.running:
            try:
                # Get pending tasks for our agents
                agent_ids = list(self.agents.keys())
                
                query = """
                    SELECT id, agent_id FROM tasks 
                    WHERE status = $1 AND agent_id = ANY($2)
                    ORDER BY created_at ASC
                    LIMIT 10
                """
                
                pending_tasks = await db_manager.fetch_all(
                    query, TaskStatus.PENDING, agent_ids
                )
                
                # Process tasks
                for task_data in pending_tasks:
                    task_id = task_data["id"]
                    agent_id = task_data["agent_id"]
                    
                    if agent_id in self.agents:
                        # Mark as assigned
                        await db_manager.execute(
                            """UPDATE tasks 
                               SET status = $1, assigned_at = CURRENT_TIMESTAMP,
                                   updated_at = CURRENT_TIMESTAMP 
                               WHERE id = $2""",
                            TaskStatus.ASSIGNED, task_id
                        )
                        
                        # Process in background
                        asyncio.create_task(
                            self._process_task(task_id, agent_id)
                        )
                
                await asyncio.sleep(self.poll_interval)
                
            except Exception as e:
                logger.error("Error in task polling", error=str(e))
                await asyncio.sleep(self.poll_interval)
    
    async def _process_task(self, task_id: int, agent_id: str):
        """Process a single task"""
        try:
            agent = self.agents[agent_id]
            success = await agent.run_task(task_id)
            
            if success:
                logger.info("Task processed successfully", 
                           task_id=task_id, agent_id=agent_id)
            else:
                logger.error("Task processing failed", 
                           task_id=task_id, agent_id=agent_id)
                           
        except Exception as e:
            logger.error("Error processing task", 
                        task_id=task_id, agent_id=agent_id, error=str(e))


# Utility functions for agent development
async def create_mock_artifacts(task_id: int, artifacts_data: Dict[str, Dict]):
    """Helper function to create mock artifacts for testing"""
    for name, data in artifacts_data.items():
        query = """
            INSERT INTO artifacts (task_id, name, schema_id, payload)
            VALUES ($1, $2, $3, $4)
        """
        
        await db_manager.execute(
            query, 
            task_id, 
            name, 
            data.get("schema_id", "test_schema_v1.0"),
            data.get("payload", {})
        )


async def get_job_context(job_id: int) -> Optional[Dict]:
    """Get complete job context including all tasks and artifacts"""
    # Get job info
    job_query = "SELECT * FROM jobs WHERE id = $1"
    job_data = await db_manager.fetch_one(job_query, job_id)
    
    if not job_data:
        return None
    
    # Get all tasks for this job
    tasks_query = """
        SELECT * FROM tasks 
        WHERE job_id = $1 
        ORDER BY created_at ASC
    """
    tasks_data = await db_manager.fetch_all(tasks_query, job_id)
    
    # Get all artifacts for this job
    artifacts_query = """
        SELECT a.*, t.agent_id 
        FROM artifacts a
        JOIN tasks t ON a.task_id = t.id
        WHERE t.job_id = $1
        ORDER BY a.created_at ASC
    """
    artifacts_data = await db_manager.fetch_all(artifacts_query, job_id)
    
    return {
        "job": job_data,
        "tasks": tasks_data,
        "artifacts": artifacts_data
    }