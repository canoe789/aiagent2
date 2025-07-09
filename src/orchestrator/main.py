"""
Main orchestrator for Project HELIX v2.0
State-driven workflow orchestration using PostgreSQL polling
"""

import asyncio
import json
import structlog
from datetime import datetime
from typing import Dict, List, Optional

from src.database.connection import get_global_db_manager
from src.database.models import JobStatus, TaskStatus, Task, Job
from src.orchestrator.workflow_engine import WorkflowEngine
from src.api.settings import settings

logger = structlog.get_logger(__name__)


class HelixOrchestrator:
    """
    Core orchestrator that polls PostgreSQL and drives the workflow
    Implements the state-driven orchestration pattern from README.md
    """
    
    def __init__(self):
        self.workflow_engine = WorkflowEngine()
        self.running = False
        self.poll_interval = settings.orchestrator_poll_interval
        
    async def start(self):
        """Start the orchestrator polling loop"""
        logger.info("Starting HELIX Orchestrator", poll_interval=self.poll_interval)
        
        # Connect to database
        await get_global_db_manager().connect()
        
        # Load workflow configuration
        await self.workflow_engine.load_workflows()
        
        self.running = True
        
        # Start polling loops
        await asyncio.gather(
            self._poll_new_jobs(),
            self._poll_completed_tasks(),
            self._monitor_failed_tasks()
        )
    
    async def stop(self):
        """Stop the orchestrator"""
        logger.info("Stopping HELIX Orchestrator")
        self.running = False
        await get_global_db_manager().disconnect()
    
    async def _poll_new_jobs(self):
        """Poll for new PENDING jobs and create first tasks"""
        while self.running:
            try:
                # Find pending jobs
                query = """
                    SELECT * FROM jobs 
                    WHERE status = $1 
                    ORDER BY created_at ASC
                """
                
                pending_jobs = await get_global_db_manager().fetch_all(query, JobStatus.PENDING)
                
                for job_data in pending_jobs:
                    job = Job.model_validate(job_data)
                    await self._process_new_job(job)
                
                await asyncio.sleep(self.poll_interval)
                
            except Exception as e:
                logger.error("Error in new jobs polling", error=str(e))
                await asyncio.sleep(self.poll_interval)
    
    async def _poll_completed_tasks(self):
        """Poll for completed tasks and create next tasks in workflow"""
        while self.running:
            try:
                # Find recently completed tasks that haven't been processed by orchestrator
                query = """
                    SELECT t.*, j.status as job_status 
                    FROM tasks t
                    JOIN jobs j ON t.job_id = j.id
                    WHERE t.status = $1 
                    AND j.status = $2
                    AND (t.error_log IS NULL OR t.error_log NOT LIKE '%[ORCHESTRATED]%')
                    ORDER BY t.completed_at ASC
                """
                
                completed_tasks = await get_global_db_manager().fetch_all(
                    query, TaskStatus.COMPLETED, JobStatus.IN_PROGRESS
                )
                
                for task_data in completed_tasks:
                    task = Task.model_validate(task_data)
                    await self._process_completed_task(task)
                
                await asyncio.sleep(self.poll_interval)
                
            except Exception as e:
                logger.error("Error in completed tasks polling", error=str(e))
                await asyncio.sleep(self.poll_interval)
    
    async def _monitor_failed_tasks(self):
        """Monitor failed tasks and trigger retries or Meta-Optimizer"""
        while self.running:
            try:
                # Find failed tasks that haven't exceeded retry limit
                query = """
                    SELECT * FROM tasks 
                    WHERE status = $1 
                    AND retry_count < $2
                    ORDER BY updated_at ASC
                """
                
                failed_tasks = await get_global_db_manager().fetch_all(
                    query, TaskStatus.FAILED, settings.max_retry_attempts
                )
                
                for task_data in failed_tasks:
                    task = Task.model_validate(task_data)
                    await self._process_failed_task(task)
                
                await asyncio.sleep(self.poll_interval * 2)  # Check less frequently
                
            except Exception as e:
                logger.error("Error in failed tasks monitoring", error=str(e))
                await asyncio.sleep(self.poll_interval)
    
    async def _process_new_job(self, job: Job):
        """Process a new job by creating the first task"""
        try:
            logger.info("Processing new job", job_id=job.id)
            
            # Mark job as in progress
            await get_global_db_manager().execute(
                "UPDATE jobs SET status = $1, updated_at = CURRENT_TIMESTAMP WHERE id = $2",
                JobStatus.IN_PROGRESS, job.id
            )
            
            # Create first task (AGENT_1: Creative Director)
            first_agent_id = self.workflow_engine.get_first_agent()
            
            input_data = {
                "artifacts": [],
                "params": {
                    "chat_input": job.initial_request.get("chat_input"),
                    "session_id": job.session_id
                }
            }
            
            await self._create_task(job.id, first_agent_id, input_data)
            
            logger.info("Created first task for job", 
                       job_id=job.id, agent_id=first_agent_id)
                       
        except Exception as e:
            logger.error("Failed to process new job", job_id=job.id, error=str(e))
            # Mark job as failed
            await get_global_db_manager().execute(
                "UPDATE jobs SET status = $1, error_message = $2, updated_at = CURRENT_TIMESTAMP WHERE id = $3",
                JobStatus.FAILED, str(e), job.id
            )
    
    async def _process_completed_task(self, task: Task):
        """Process a completed task and create next tasks in workflow"""
        try:
            logger.info("Processing completed task", task_id=task.id, agent_id=task.agent_id)
            
            # CRITICAL FIX: Create artifact from task output before proceeding
            await self._create_artifact(task)
            logger.info("Artifact created for completed task", task_id=task.id)
            
            # Get next agents in workflow
            next_agents = self.workflow_engine.get_next_agents(task.agent_id)
            logger.debug("Next agents determined", agent_id=task.agent_id, next_agents=next_agents)
            
            if not next_agents:
                # This was the last task, mark job as completed
                await self._complete_job(task.job_id)
            else:
                # Create next tasks
                for next_agent_id in next_agents:
                    input_data = await self._prepare_task_input(task.job_id, next_agent_id)
                    await self._create_task(task.job_id, next_agent_id, input_data)
                    
                    logger.info("Created next task", 
                               job_id=task.job_id, agent_id=next_agent_id)
            
            # CRITICAL FIX: Mark the current task as processed by orchestrator
            # This prevents infinite loop of processing the same completed task
            # Using a custom field to track orchestrator processing
            await get_global_db_manager().execute(
                """UPDATE tasks SET updated_at = CURRENT_TIMESTAMP,
                   error_log = COALESCE(error_log, '') || '[ORCHESTRATED]'
                   WHERE id = $1 AND (error_log IS NULL OR error_log NOT LIKE '%[ORCHESTRATED]%')""",
                task.id
            )
            logger.info("Task marked as orchestrated", task_id=task.id)
            
        except Exception as e:
            logger.error("Failed to process completed task", 
                        task_id=task.id, error=str(e))
            # Mark the task as FAILED so it's not re-polled by _poll_completed_tasks
            try:
                await get_global_db_manager().execute(
                    """UPDATE tasks SET status = $1, error_log = COALESCE(error_log, '') || $2, 
                       updated_at = CURRENT_TIMESTAMP WHERE id = $3""",
                    TaskStatus.FAILED, f"[ORCHESTRATION_FAILED]: {str(e)}", task.id
                )
                logger.info("Task marked as FAILED due to orchestration error", task_id=task.id)
            except Exception as inner_e:
                logger.error("Failed to mark task as FAILED", task_id=task.id, error=str(inner_e))
    
    async def _process_failed_task(self, task: Task):
        """Process a failed task - retry or escalate to Meta-Optimizer"""
        try:
            if task.retry_count < settings.max_retry_attempts:
                # Retry the task
                await get_global_db_manager().execute(
                    """UPDATE tasks 
                       SET status = $1, retry_count = retry_count + 1, 
                           updated_at = CURRENT_TIMESTAMP 
                       WHERE id = $2""",
                    TaskStatus.PENDING, task.id
                )
                
                logger.info("Retrying failed task", 
                           task_id=task.id, retry_count=task.retry_count + 1)
            else:
                # Escalate to Meta-Optimizer (AGENT_5)
                # Create system failure case artifact for AGENT_5
                await self._create_system_failure_case(task)
                
                # Get AGENT_5 input artifacts including the system failure case
                input_data = await self._prepare_task_input(task.job_id, "AGENT_5")
                
                await self._create_task(task.job_id, "AGENT_5", input_data)
                
                # Mark original job as failed
                await get_global_db_manager().execute(
                    "UPDATE jobs SET status = $1, updated_at = CURRENT_TIMESTAMP WHERE id = $2",
                    JobStatus.FAILED, task.job_id
                )
                
                logger.info("Escalated to Meta-Optimizer", 
                           job_id=task.job_id, failed_task_id=task.id)
                           
        except Exception as e:
            logger.error("Failed to process failed task", 
                        task_id=task.id, error=str(e))
    
    async def _create_task(self, job_id: int, agent_id: str, input_data: Dict):
        """Create a new task in the database"""
        query = """
            INSERT INTO tasks (job_id, agent_id, status, input_data)
            VALUES ($1, $2, $3, $4)
            RETURNING id
        """
        
        result = await get_global_db_manager().fetch_one(
            query, job_id, agent_id, TaskStatus.PENDING, input_data
        )
        
        return result["id"] if result else None
    
    async def _create_artifact(self, task: Task):
        """Create artifact from task output"""
        if not task.output_data:
            logger.warning("No output data for task", task_id=task.id)
            return
            
        schema_id = task.output_data.get("schema_id")
        payload = task.output_data.get("payload", {})
        
        # Get artifact name from workflow definition
        agent_def = self.workflow_engine.agent_definitions.get(task.agent_id, {})
        artifact_name = agent_def.get("output_artifact")
        
        if not artifact_name:
            logger.error("No output artifact defined for agent", agent_id=task.agent_id)
            return
            
        if schema_id and payload:
            # Validate payload format for PresentationBlueprint
            if schema_id == "PresentationBlueprint_v1.0":
                if isinstance(payload, str) and payload.strip().startswith('<!DOCTYPE html>'):
                    logger.error("PresentationBlueprint payload is HTML string instead of JSON", 
                                task_id=task.id, payload_preview=payload[:100])
                    # Try to recover by creating a minimal valid blueprint
                    payload = {
                        "narrative_structure": {},
                        "content_sections": [],
                        "storytelling_elements": {},
                        "engagement_strategy": {},
                        "metadata": {
                            "error": "Invalid payload format - HTML string instead of JSON",
                            "recovery": "Generated minimal valid blueprint"
                        }
                    }
                elif not isinstance(payload, dict):
                    logger.error("PresentationBlueprint payload is not a dict", 
                                task_id=task.id, payload_type=type(payload).__name__)
                    payload = {
                        "narrative_structure": {},
                        "content_sections": [],
                        "storytelling_elements": {},
                        "engagement_strategy": {},
                        "metadata": {
                            "error": f"Invalid payload type: {type(payload).__name__}",
                            "recovery": "Generated minimal valid blueprint"
                        }
                    }
            
            query = """
                INSERT INTO artifacts (task_id, name, schema_id, payload)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (task_id, name) DO NOTHING
            """
            
            await get_global_db_manager().execute(query, task.id, artifact_name, schema_id, payload)
            logger.info("Artifact created or already exists", task_id=task.id, artifact_name=artifact_name, schema_id=schema_id)
        else:
            logger.error("Missing schema_id or payload for artifact creation", 
                        task_id=task.id, schema_id=schema_id, has_payload=bool(payload))
    
    async def _prepare_task_input(self, job_id: int, agent_id: str) -> Dict:
        """Prepare input data for a task based on required artifacts"""
        required_artifacts = self.workflow_engine.get_agent_input_artifacts(agent_id)
        
        artifacts = []
        for artifact_name in required_artifacts:
            # Find the most recent artifact with this name for this job
            query = """
                SELECT t.id as source_task_id
                FROM artifacts a
                JOIN tasks t ON a.task_id = t.id
                WHERE t.job_id = $1 AND a.name = $2
                ORDER BY a.created_at DESC
                LIMIT 1
            """
            
            result = await get_global_db_manager().fetch_one(query, job_id, artifact_name)
            if result:
                artifacts.append({
                    "name": artifact_name,
                    "source_task_id": result["source_task_id"]
                })
        
        return {
            "artifacts": artifacts,
            "params": {}
        }
    
    async def _complete_job(self, job_id: int):
        """Mark a job as completed"""
        await get_global_db_manager().execute(
            """UPDATE jobs 
               SET status = $1, completed_at = CURRENT_TIMESTAMP, 
                   updated_at = CURRENT_TIMESTAMP 
               WHERE id = $2""",
            JobStatus.COMPLETED, job_id
        )
        
        logger.info("Job completed", job_id=job_id)
    
    async def _create_system_failure_case(self, failed_task: Task):
        """Create a system failure case artifact for AGENT_5 analysis"""
        try:
            # Gather failure information from the database
            failure_analysis = await self._analyze_task_failure(failed_task)
            
            # Create system failure case payload
            system_failure_case = {
                "failure_instances": [
                    {
                        "task_id": failed_task.id,
                        "job_id": failed_task.job_id,
                        "agent_id": failed_task.agent_id,
                        "failure_timestamp": failed_task.updated_at.isoformat() if failed_task.updated_at else None,
                        "error_message": failed_task.error_log,
                        "retry_count": failed_task.retry_count,
                        "failure_type": "task_execution_failure"
                    }
                ],
                "job_context": failure_analysis["job_context"],
                "system_state": failure_analysis["system_state"],
                "pattern_indicators": failure_analysis["pattern_indicators"]
            }
            
            # Create the artifact in the database
            query = """
                INSERT INTO artifacts (task_id, name, schema_id, payload, created_at)
                VALUES ($1, $2, $3, $4, CURRENT_TIMESTAMP)
                RETURNING id
            """
            
            result = await get_global_db_manager().fetch_one(
                query,
                failed_task.id,
                "system_failure_case",
                "SystemFailureCase_v1.0",
                system_failure_case
            )
            
            if result:
                logger.info("System failure case artifact created", 
                           artifact_id=result["id"], failed_task_id=failed_task.id)
            else:
                logger.error("Failed to create system failure case artifact", 
                           failed_task_id=failed_task.id)
                
        except Exception as e:
            logger.error("Error creating system failure case", 
                        failed_task_id=failed_task.id, error=str(e))
    
    async def _analyze_task_failure(self, failed_task: Task) -> Dict:
        """Analyze the failure context for AGENT_5"""
        try:
            # Get job details
            job_query = "SELECT * FROM jobs WHERE id = $1"
            job_data = await get_global_db_manager().fetch_one(job_query, failed_task.job_id)
            
            # Get all tasks for this job to understand the failure context
            tasks_query = """
                SELECT agent_id, status, error_log, retry_count, created_at, completed_at
                FROM tasks 
                WHERE job_id = $1 
                ORDER BY created_at ASC
            """
            job_tasks = await get_global_db_manager().fetch_all(tasks_query, failed_task.job_id)
            
            # Build failure analysis
            return {
                "job_context": {
                    "job_id": failed_task.job_id,
                    "initial_request": job_data["initial_request"] if job_data else {},
                    "job_status": job_data["status"] if job_data else "unknown",
                    "total_tasks": len(job_tasks),
                    "failed_agent": failed_task.agent_id
                },
                "system_state": {
                    "task_sequence": [
                        {
                            "agent_id": task["agent_id"],
                            "status": task["status"],
                            "has_error": bool(task["error_log"]),
                            "retry_count": task["retry_count"]
                        } for task in job_tasks
                    ]
                },
                "pattern_indicators": {
                    "repeated_agent_failures": sum(1 for task in job_tasks 
                                                  if task["agent_id"] == failed_task.agent_id and task["error_log"]),
                    "workflow_interruption_point": failed_task.agent_id,
                    "max_retry_exceeded": failed_task.retry_count >= 3
                }
            }
            
        except Exception as e:
            logger.error("Error analyzing task failure", error=str(e))
            return {
                "job_context": {"error": "Failed to analyze job context"},
                "system_state": {"error": "Failed to analyze system state"},
                "pattern_indicators": {"error": "Failed to analyze patterns"}
            }


async def main():
    """Main entry point for the orchestrator"""
    # Configure logging
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
            structlog.processors.JSONRenderer()
        ],
        logger_factory=structlog.WriteLoggerFactory(),
        wrapper_class=structlog.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    orchestrator = HelixOrchestrator()
    
    try:
        await orchestrator.start()
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    finally:
        await orchestrator.stop()


if __name__ == "__main__":
    asyncio.run(main())