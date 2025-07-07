"""
Main orchestrator for Project HELIX v2.0
State-driven workflow orchestration using PostgreSQL polling
"""

import asyncio
import json
import structlog
from datetime import datetime
from typing import Dict, List, Optional

from src.database.connection import db_manager
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
        await db_manager.connect()
        
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
        await db_manager.disconnect()
    
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
                
                pending_jobs = await db_manager.fetch_all(query, JobStatus.PENDING)
                
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
                # Find recently completed tasks
                query = """
                    SELECT t.*, j.status as job_status 
                    FROM tasks t
                    JOIN jobs j ON t.job_id = j.id
                    WHERE t.status = $1 
                    AND j.status = $2
                    ORDER BY t.completed_at ASC
                """
                
                completed_tasks = await db_manager.fetch_all(
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
                
                failed_tasks = await db_manager.fetch_all(
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
            await db_manager.execute(
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
            await db_manager.execute(
                "UPDATE jobs SET status = $1, error_message = $2, updated_at = CURRENT_TIMESTAMP WHERE id = $3",
                JobStatus.FAILED, str(e), job.id
            )
    
    async def _process_completed_task(self, task: Task):
        """Process a completed task and create next tasks in workflow"""
        try:
            logger.info("Processing completed task", task_id=task.id, agent_id=task.agent_id)
            
            # Get next agents in workflow
            next_agents = self.workflow_engine.get_next_agents(task.agent_id)
            
            if not next_agents:
                # This was the last task, mark job as completed
                await self._complete_job(task.job_id)
                return
            
            # Create artifacts from task output
            if task.output_data:
                await self._create_artifact(task)
            
            # Create next tasks
            for next_agent_id in next_agents:
                input_data = await self._prepare_task_input(task.job_id, next_agent_id)
                await self._create_task(task.job_id, next_agent_id, input_data)
                
                logger.info("Created next task", 
                           job_id=task.job_id, agent_id=next_agent_id)
            
        except Exception as e:
            logger.error("Failed to process completed task", 
                        task_id=task.id, error=str(e))
    
    async def _process_failed_task(self, task: Task):
        """Process a failed task - retry or escalate to Meta-Optimizer"""
        try:
            if task.retry_count < settings.max_retry_attempts:
                # Retry the task
                await db_manager.execute(
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
                input_data = {
                    "artifacts": [],
                    "params": {"failed_job_id": task.job_id}
                }
                
                await self._create_task(task.job_id, "AGENT_5", input_data)
                
                # Mark original job as failed
                await db_manager.execute(
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
        
        result = await db_manager.fetch_one(
            query, job_id, agent_id, TaskStatus.PENDING, input_data
        )
        
        return result["id"] if result else None
    
    async def _create_artifact(self, task: Task):
        """Create artifact from task output"""
        if not task.output_data:
            return
            
        schema_id = task.output_data.get("schema_id")
        payload = task.output_data.get("payload", {})
        artifact_name = self.workflow_engine.get_agent_output_artifact(task.agent_id)
        
        if schema_id and artifact_name:
            query = """
                INSERT INTO artifacts (task_id, name, schema_id, payload)
                VALUES ($1, $2, $3, $4)
            """
            
            await db_manager.execute(query, task.id, artifact_name, schema_id, payload)
    
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
            
            result = await db_manager.fetch_one(query, job_id, artifact_name)
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
        await db_manager.execute(
            """UPDATE jobs 
               SET status = $1, completed_at = CURRENT_TIMESTAMP, 
                   updated_at = CURRENT_TIMESTAMP 
               WHERE id = $2""",
            JobStatus.COMPLETED, job_id
        )
        
        logger.info("Job completed", job_id=job_id)


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