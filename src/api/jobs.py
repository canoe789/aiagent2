"""
Job management endpoints for Project HELIX v2.0
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional, List
import structlog
from datetime import datetime

from src.database.connection import get_db_connection
from src.database.models import (
    JobCreate, JobResponse, Job, Task, JobStatus, TaskStatus, TaskResponse
)

logger = structlog.get_logger(__name__)
jobs_router = APIRouter(tags=["Jobs"])


@jobs_router.post("/jobs", response_model=JobResponse)
async def create_job(
    job_data: JobCreate,
    db_manager=Depends(get_db_connection)
):
    """Create a new creative production job"""
    try:
        # Prepare initial request data
        initial_request = {
            "chat_input": job_data.chat_input,
            "session_id": job_data.session_id,
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Insert job into database
        query = """
            INSERT INTO jobs (status, initial_request, session_id)
            VALUES ($1, $2, $3)
            RETURNING id
        """
        
        result = await db_manager.fetch_one(
            query,
            JobStatus.PENDING,
            initial_request,
            job_data.session_id
        )
        
        if not result:
            raise HTTPException(status_code=500, detail="Failed to create job")
        
        job_id = result["id"]
        
        logger.info("Job created successfully", job_id=job_id, session_id=job_data.session_id)
        
        return JobResponse(
            job_id=job_id,
            status=JobStatus.PENDING,
            message="Job created successfully and queued for processing",
            created_at=datetime.utcnow(),
            error_message=None,
            tasks=[]
        )
        
    except Exception as e:
        logger.error("Failed to create job", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@jobs_router.get("/jobs/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: int,
    db_manager=Depends(get_db_connection)
):
    """Get job details by ID with associated tasks"""
    try:
        # Get job details
        job_query = "SELECT * FROM jobs WHERE id = $1"
        job_result = await db_manager.fetch_one(job_query, job_id)
        
        if not job_result:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Get associated tasks
        tasks_query = """
            SELECT id, status, agent_id, created_at, started_at, completed_at, error_log
            FROM tasks 
            WHERE job_id = $1 
            ORDER BY created_at ASC
        """
        task_results = await db_manager.fetch_all(tasks_query, job_id)
        
        # Convert tasks to TaskResponse objects
        tasks = [
            TaskResponse(
                task_id=task["id"],
                status=task["status"],
                agent_id=task["agent_id"],
                created_at=task["created_at"],
                started_at=task["started_at"],
                completed_at=task["completed_at"],
                error_log=task["error_log"]
            )
            for task in task_results
        ]
        
        return JobResponse(
            job_id=job_result["id"],
            status=job_result["status"],
            message=f"Job {job_result['status'].lower()}",
            created_at=job_result["created_at"],
            error_message=job_result["error_message"],
            tasks=tasks
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get job", job_id=job_id, error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@jobs_router.get("/jobs", response_model=List[Job])
async def list_jobs(
    status: Optional[JobStatus] = None,
    session_id: Optional[str] = None,
    limit: int = Query(default=50, le=100),
    offset: int = Query(default=0, ge=0),
    db_manager=Depends(get_db_connection)
):
    """List jobs with optional filtering"""
    try:
        # Build query based on filters
        where_clauses = []
        params = []
        param_count = 0
        
        if status:
            param_count += 1
            where_clauses.append(f"status = ${param_count}")
            params.append(status)
        
        if session_id:
            param_count += 1
            where_clauses.append(f"session_id = ${param_count}")
            params.append(session_id)
        
        where_clause = " WHERE " + " AND ".join(where_clauses) if where_clauses else ""
        
        query = f"""
            SELECT * FROM jobs
            {where_clause}
            ORDER BY created_at DESC
            LIMIT ${param_count + 1} OFFSET ${param_count + 2}
        """
        
        params.extend([limit, offset])
        results = await db_manager.fetch_all(query, *params)
        
        return [Job.model_validate(result) for result in results]
        
    except Exception as e:
        logger.error("Failed to list jobs", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@jobs_router.get("/jobs/{job_id}/tasks", response_model=List[Task])
async def get_job_tasks(
    job_id: int,
    db_manager=Depends(get_db_connection)
):
    """Get all tasks for a specific job"""
    try:
        # Verify job exists
        job_query = "SELECT id FROM jobs WHERE id = $1"
        job_result = await db_manager.fetch_one(job_query, job_id)
        
        if not job_result:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Get tasks
        tasks_query = """
            SELECT * FROM tasks 
            WHERE job_id = $1 
            ORDER BY created_at ASC
        """
        
        results = await db_manager.fetch_all(tasks_query, job_id)
        return [Task.model_validate(result) for result in results]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get job tasks", job_id=job_id, error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@jobs_router.delete("/jobs/{job_id}")
async def cancel_job(
    job_id: int,
    db_manager=Depends(get_db_connection)
):
    """Cancel a job (if not completed)"""
    try:
        # Check current status
        check_query = "SELECT status FROM jobs WHERE id = $1"
        result = await db_manager.fetch_one(check_query, job_id)
        
        if not result:
            raise HTTPException(status_code=404, detail="Job not found")
        
        if result["status"] in [JobStatus.COMPLETED, JobStatus.CANCELLED]:
            raise HTTPException(
                status_code=400, 
                detail=f"Cannot cancel job with status: {result['status']}"
            )
        
        # Update job status
        update_query = """
            UPDATE jobs 
            SET status = $1, updated_at = CURRENT_TIMESTAMP 
            WHERE id = $2
        """
        
        await db_manager.execute(update_query, JobStatus.CANCELLED, job_id)
        
        logger.info("Job cancelled", job_id=job_id)
        return {"message": "Job cancelled successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to cancel job", job_id=job_id, error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")