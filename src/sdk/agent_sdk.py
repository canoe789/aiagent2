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

from src.database.connection import get_global_db_manager
from src.database.models import (
    Task, TaskStatus, TaskInput, TaskOutput, 
    Artifact, AgentPrompt
)
from src.exceptions import classify_error, RetryableError
from src.config import config

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
        Execute a specific task from the database with retry support
        Implements P4: Idempotence & Recoverability
        
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
            
            # Check if task already completed (idempotency)
            if task.status == TaskStatus.COMPLETED:
                logger.info("Task already completed, skipping", 
                           task_id=task_id, agent_id=self.agent_id)
                return True
            
            # Implement retry logic
            max_retries = config.agent.max_retry_count
            retry_delay = config.agent.retry_delay_seconds
            
            for attempt in range(max_retries):
                try:
                    # Mark task as in progress (only on first attempt or retry)
                    if attempt == 0 or task.status == TaskStatus.RETRYING:
                        await self.update_task_status(task_id, TaskStatus.IN_PROGRESS)
                    
                    logger.info("Starting task processing", 
                               task_id=task_id, agent_id=self.agent_id,
                               attempt=attempt + 1, max_retries=max_retries)
                    
                    # Parse task input
                    task_input = TaskInput.model_validate(task.input_data)
                    
                    # Process the task
                    task_output = await self.process_task(task_input)
                    
                    # Save output and complete task atomically
                    await self.save_output_and_complete_task(task_id, task_output)
                    
                    logger.info("Task completed successfully", 
                               task_id=task_id, agent_id=self.agent_id,
                               attempt=attempt + 1)
                    
                    return True
                    
                except Exception as e:
                    # Check if error is retryable
                    is_retryable = classify_error(e)
                    
                    if is_retryable and attempt < max_retries - 1:
                        logger.warning("Retryable error occurred, will retry", 
                                      task_id=task_id, agent_id=self.agent_id,
                                      attempt=attempt + 1, error=str(e),
                                      retry_in_seconds=retry_delay)
                        
                        # Update retry count and status
                        await self._increment_retry_count(task_id)
                        await self.update_task_status(task_id, TaskStatus.RETRYING, str(e))
                        
                        # Exponential backoff
                        await asyncio.sleep(retry_delay * (2 ** attempt))
                        
                        # Refresh task state for next attempt
                        task = await self.get_task(task_id)
                        self.current_task = task
                        
                    else:
                        # Non-retryable error or max retries reached
                        logger.error("Task processing failed", 
                                    task_id=task_id, agent_id=self.agent_id, 
                                    error=str(e), is_retryable=is_retryable,
                                    attempts=attempt + 1)
                        
                        # Mark task as failed and log error
                        await self.update_task_status(task_id, TaskStatus.FAILED, str(e))
                        return False
            
        except Exception as e:
            logger.error("Unexpected error in task runner", 
                        task_id=task_id, agent_id=self.agent_id, error=str(e))
            await self.update_task_status(task_id, TaskStatus.FAILED, str(e))
            return False
    
    async def get_task(self, task_id: int) -> Optional[Task]:
        """Get task details from database"""
        query = "SELECT * FROM tasks WHERE id = $1"
        result = await get_global_db_manager().fetch_one(query, task_id)
        return Task.model_validate(result) if result else None
    
    async def update_task_status(self, task_id: int, status: TaskStatus, error_log: Optional[str] = None):
        """Update task status in database"""
        if status == TaskStatus.IN_PROGRESS:
            query = """
                UPDATE tasks 
                SET status = $1, started_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
                WHERE id = $2
            """
            await get_global_db_manager().execute(query, status, task_id)
        elif status == TaskStatus.COMPLETED:
            query = """
                UPDATE tasks 
                SET status = $1, completed_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
                WHERE id = $2
            """
            await get_global_db_manager().execute(query, status, task_id)
        elif status == TaskStatus.FAILED:
            query = """
                UPDATE tasks 
                SET status = $1, error_log = $2, updated_at = CURRENT_TIMESTAMP
                WHERE id = $3
            """
            await get_global_db_manager().execute(query, status, error_log, task_id)
        elif status == TaskStatus.RETRYING:
            query = """
                UPDATE tasks 
                SET status = $1, error_log = $2, updated_at = CURRENT_TIMESTAMP
                WHERE id = $3
            """
            await get_global_db_manager().execute(query, status, error_log, task_id)
    
    async def _increment_retry_count(self, task_id: int):
        """Increment the retry count for a task"""
        query = """
            UPDATE tasks 
            SET retry_count = retry_count + 1, updated_at = CURRENT_TIMESTAMP
            WHERE id = $1
        """
        await get_global_db_manager().execute(query, task_id)
    
    async def save_output_and_complete_task(self, task_id: int, output: TaskOutput):
        """
        Atomically save task output and mark task as completed
        This fixes the transaction boundary issue by ensuring both operations
        happen in the same database transaction
        """
        try:
            # Validate output against schema before saving
            import jsonschema
            from src.config import config
            
            # Get schema path from configuration
            schema_path = config.paths.get_schema_path(output.schema_id)
            if not schema_path.exists():
                raise ValueError(f"Schema file not found for schema_id: {output.schema_id}")
            
            with open(schema_path, 'r') as f:
                schema = json.load(f)
            
            # Validate the payload against the schema
            jsonschema.validate(instance=output.payload, schema=schema)
            logger.info("Output payload validated successfully against schema", 
                       task_id=task_id, schema_id=output.schema_id)
            
            # Get artifact name for this agent (workflow mapping)
            artifact_name = self._get_artifact_name_for_agent()
            
            # Execute all operations in a single transaction
            async with get_global_db_manager().pool.acquire() as conn:
                async with conn.transaction():
                    # 1. Save output to tasks table
                    await conn.execute(
                        """UPDATE tasks 
                           SET output_data = $1, updated_at = CURRENT_TIMESTAMP
                           WHERE id = $2""",
                        output.model_dump(), task_id
                    )
                    
                    # 2. Create artifact entry with validation
                    payload = output.payload
                    
                    # Validate PresentationBlueprint format
                    if output.schema_id == "PresentationBlueprint_v1.0":
                        if isinstance(payload, str) and payload.strip().startswith('<!DOCTYPE html>'):
                            logger.error("Agent returned HTML string for PresentationBlueprint", 
                                       agent_id=self.agent_id, task_id=task_id)
                            raise ValueError("PresentationBlueprint must be JSON object, not HTML string")
                        elif not isinstance(payload, dict):
                            logger.error("Agent returned invalid type for PresentationBlueprint", 
                                       agent_id=self.agent_id, task_id=task_id, 
                                       payload_type=type(payload).__name__)
                            raise ValueError(f"PresentationBlueprint must be dict, not {type(payload).__name__}")
                    
                    await conn.execute(
                        """INSERT INTO artifacts (task_id, name, schema_id, payload)
                           VALUES ($1, $2, $3, $4)""",
                        task_id, artifact_name, output.schema_id, payload
                    )
                    
                    # 3. Mark task as completed
                    await conn.execute(
                        """UPDATE tasks 
                           SET status = $1, completed_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
                           WHERE id = $2""",
                        TaskStatus.COMPLETED, task_id
                    )
            
            logger.info("Task output and completion saved atomically", 
                       task_id=task_id, schema_id=output.schema_id, artifact_name=artifact_name)
                       
        except jsonschema.ValidationError as ve:
            logger.error("Schema validation failed for task output", 
                         task_id=task_id, schema_id=output.schema_id, error=str(ve))
            raise ValueError(f"Output schema validation failed: {str(ve)}") from ve
        except Exception as e:
            logger.error("Failed to save task output and complete task atomically", 
                         task_id=task_id, error=str(e))
            raise
    
    def _get_artifact_name_for_agent(self) -> str:
        """Get the artifact name produced by this agent based on workflow mapping"""
        agent_artifact_map = {
            "AGENT_1": "creative_brief",
            "AGENT_2": "visual_explorations", 
            "AGENT_3": "presentation_blueprint",
            "AGENT_4": "audit_report",
            "AGENT_5": "evolution_proposal"
        }
        return agent_artifact_map.get(self.agent_id, f"artifact_{self.agent_id.lower()}")
    
    async def get_agent_prompt(self, version: str = "v0") -> Optional[str]:
        """
        Get agent prompt from database (P3: Externalized Cognition)
        
        Args:
            version: Prompt version to retrieve (default: "v0" for new tasks)
                    Special values:
                    - "v0": Base version for new tasks
                    - "latest": Most recently active version
                    - Specific version string: e.g., "v20240115_123456"
            
        Returns:
            Optional[str]: The prompt text if found, None otherwise
        """
        try:
            if version == "latest":
                # Get the most recent active version
                query = """
                    SELECT prompt_text FROM agent_prompts 
                    WHERE agent_id = $1 AND is_active = true
                    ORDER BY created_at DESC
                    LIMIT 1
                """
                result = await get_global_db_manager().fetch_one(query, self.agent_id)
            else:
                # Get specific version
                query = """
                    SELECT prompt_text FROM agent_prompts 
                    WHERE agent_id = $1 AND version = $2
                    LIMIT 1
                """
                result = await get_global_db_manager().fetch_one(query, self.agent_id, version)
            
            if result:
                logger.info("Agent prompt retrieved", 
                           agent_id=self.agent_id, version=version)
                return result['prompt_text']
            else:
                # If v0 not found, fall back to latest
                if version == "v0":
                    logger.warning("Base version v0 not found, falling back to latest", 
                                  agent_id=self.agent_id)
                    return await self.get_agent_prompt("latest")
                
                logger.warning("Agent prompt not found in database", 
                              agent_id=self.agent_id, version=version)
                return None
                
        except Exception as e:
            logger.error("Failed to retrieve agent prompt", 
                        agent_id=self.agent_id, version=version, error=str(e))
            return None
    
    async def save_agent_prompt(self, prompt_text: str, version: Optional[str] = None, 
                               created_by: str = "system") -> bool:
        """
        Save or update agent prompt in database
        
        Args:
            prompt_text: The prompt text to save
            version: Version identifier (auto-generated if not provided)
            created_by: Who created/updated this prompt
            
        Returns:
            bool: True if saved successfully, False otherwise
        """
        try:
            if not version:
                # Auto-generate version based on timestamp
                from datetime import datetime
                version = f"v{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Deactivate previous versions if this is a new latest (not v0)
            if version != "v0":
                deactivate_query = """
                    UPDATE agent_prompts 
                    SET is_active = false
                    WHERE agent_id = $1 AND is_active = true AND version != 'v0'
                """
                await get_global_db_manager().execute(deactivate_query, self.agent_id)
            
            # Check if prompt exists
            existing = await get_global_db_manager().fetch_one(
                "SELECT id FROM agent_prompts WHERE agent_id = $1 AND version = $2",
                self.agent_id, version
            )
            
            # Determine if this version should be active
            is_active = version != "v0"  # v0 is never active, it's the base version
            
            if existing:
                # Update existing prompt
                query = """
                    UPDATE agent_prompts 
                    SET prompt_text = $1, created_by = $2, is_active = $3, created_at = CURRENT_TIMESTAMP
                    WHERE agent_id = $4 AND version = $5
                """
                await get_global_db_manager().execute(
                    query, prompt_text, created_by, is_active, self.agent_id, version
                )
                logger.info("Agent prompt updated", 
                           agent_id=self.agent_id, version=version)
            else:
                # Insert new prompt
                query = """
                    INSERT INTO agent_prompts (agent_id, version, prompt_text, is_active, created_by)
                    VALUES ($1, $2, $3, $4, $5)
                """
                await get_global_db_manager().execute(
                    query, self.agent_id, version, prompt_text, is_active, created_by
                )
                logger.info("Agent prompt created", 
                           agent_id=self.agent_id, version=version)
            
            return True
            
        except Exception as e:
            logger.error("Failed to save agent prompt", 
                        agent_id=self.agent_id, version=version, error=str(e))
            return False
    
    async def rollback_prompt_version(self, target_version: str = "v0") -> bool:
        """
        Rollback to a specific prompt version
        
        Args:
            target_version: Version to rollback to (default: "v0")
            
        Returns:
            bool: True if rollback successful, False otherwise
        """
        try:
            # Deactivate all versions
            deactivate_query = """
                UPDATE agent_prompts 
                SET is_active = false
                WHERE agent_id = $1
            """
            await get_global_db_manager().execute(deactivate_query, self.agent_id)
            
            # Activate target version (unless it's v0)
            if target_version != "v0":
                activate_query = """
                    UPDATE agent_prompts 
                    SET is_active = true
                    WHERE agent_id = $1 AND version = $2
                """
                await get_global_db_manager().execute(activate_query, self.agent_id, target_version)
            
            logger.info("Prompt version rolled back", 
                       agent_id=self.agent_id, target_version=target_version)
            return True
            
        except Exception as e:
            logger.error("Failed to rollback prompt version", 
                        agent_id=self.agent_id, target_version=target_version, error=str(e))
            return False
    
    async def clear_prompt_versions(self, keep_versions: List[str] = ["v0"]) -> bool:
        """
        Clear all prompt versions except specified ones
        
        Args:
            keep_versions: List of versions to keep (default: ["v0"])
            
        Returns:
            bool: True if cleared successfully, False otherwise
        """
        try:
            placeholders = ",".join([f"${i+2}" for i in range(len(keep_versions))])
            query = f"""
                DELETE FROM agent_prompts 
                WHERE agent_id = $1 AND version NOT IN ({placeholders})
            """
            
            await get_global_db_manager().execute(query, self.agent_id, *keep_versions)
            
            logger.info("Prompt versions cleared", 
                       agent_id=self.agent_id, kept_versions=keep_versions)
            return True
            
        except Exception as e:
            logger.error("Failed to clear prompt versions", 
                        agent_id=self.agent_id, error=str(e))
            return False
    
    async def log_system_event(self, event_type: str, message: str, 
                              details: Optional[Dict[str, Any]] = None):
        """Log system events for monitoring and debugging"""
        try:
            query = """
                INSERT INTO system_logs (agent_id, event_type, message, details)
                VALUES ($1, $2, $3, $4)
            """
            await get_global_db_manager().execute(
                query, self.agent_id, event_type, message, details or {}
            )
        except Exception as e:
            logger.error("Failed to log system event", error=str(e))
    
    async def claim_next_task(self) -> Optional[int]:
        """
        Claim the next available task for this agent
        Uses SELECT FOR UPDATE SKIP LOCKED to prevent race conditions
        
        Returns:
            Optional[int]: Task ID if a task was claimed, None otherwise
        """
        try:
            async with get_global_db_manager().pool.acquire() as conn:
                async with conn.transaction():
                    # Use SELECT FOR UPDATE SKIP LOCKED to atomically claim a task
                    result = await conn.fetchrow("""
                        SELECT id FROM tasks 
                        WHERE agent_id = $1 
                        AND status = 'PENDING'
                        ORDER BY created_at ASC
                        LIMIT 1
                        FOR UPDATE SKIP LOCKED
                    """, self.agent_id)
                    
                    if result:
                        task_id = result['id']
                        # Mark as assigned to prevent other workers from taking it
                        await conn.execute("""
                            UPDATE tasks 
                            SET status = 'ASSIGNED', 
                                assigned_at = CURRENT_TIMESTAMP,
                                updated_at = CURRENT_TIMESTAMP
                            WHERE id = $1
                        """, task_id)
                        
                        logger.info("Task claimed successfully", 
                                   task_id=task_id, agent_id=self.agent_id)
                        return task_id
                    
            return None
            
        except Exception as e:
            logger.error("Failed to claim task", 
                        agent_id=self.agent_id, error=str(e))
            return None
    
    async def save_task_output(self, task_id: int, output: TaskOutput):
        """Save task output to database with schema validation"""
        try:
            # Validate output against schema before saving
            import jsonschema
            import os
            
            # Load the schema file (from src/sdk/ to project root)
            schema_path = os.path.join(os.path.dirname(__file__), "..", "..", "schemas", f"{output.schema_id}.json")
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
            await get_global_db_manager().execute(query, output.model_dump(), task_id)
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
        
        results = await get_global_db_manager().fetch_all(query, task_ids, names)
        
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
    
    # Removed duplicate get_agent_prompt method - using the one at line 264
    
    async def log_system_event(self, level: str, message: str, metadata: Optional[Dict] = None):
        """Log a system event"""
        import json
        
        query = """
            INSERT INTO system_logs (level, component, message, metadata)
            VALUES ($1, $2, $3, $4::jsonb)
        """
        
        metadata_json = json.dumps(metadata or {})
        
        await get_global_db_manager().execute(
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
        
        await get_global_db_manager().connect()
        self.running = True
        
        # Start polling loop
        await self._poll_tasks()
    
    async def stop(self):
        """Stop the worker"""
        logger.info("Stopping agent worker")
        self.running = False
        await get_global_db_manager().disconnect()
    
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
                
                pending_tasks = await get_global_db_manager().fetch_all(
                    query, TaskStatus.PENDING, agent_ids
                )
                
                # Process tasks
                for task_data in pending_tasks:
                    task_id = task_data["id"]
                    agent_id = task_data["agent_id"]
                    
                    if agent_id in self.agents:
                        # Mark as assigned
                        await get_global_db_manager().execute(
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
        
        await get_global_db_manager().execute(
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
    job_data = await get_global_db_manager().fetch_one(job_query, job_id)
    
    if not job_data:
        return None
    
    # Get all tasks for this job
    tasks_query = """
        SELECT * FROM tasks 
        WHERE job_id = $1 
        ORDER BY created_at ASC
    """
    tasks_data = await get_global_db_manager().fetch_all(tasks_query, job_id)
    
    # Get all artifacts for this job
    artifacts_query = """
        SELECT a.*, t.agent_id 
        FROM artifacts a
        JOIN tasks t ON a.task_id = t.id
        WHERE t.job_id = $1
        ORDER BY a.created_at ASC
    """
    artifacts_data = await get_global_db_manager().fetch_all(artifacts_query, job_id)
    
    return {
        "job": job_data,
        "tasks": tasks_data,
        "artifacts": artifacts_data
    }