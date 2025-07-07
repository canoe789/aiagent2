"""
Health check endpoints for Project HELIX v2.0
"""

from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
import structlog

from database.connection import get_db_connection

logger = structlog.get_logger(__name__)
health_router = APIRouter(tags=["Health"])


@health_router.get("/health")
async def health_check(db_manager=Depends(get_db_connection)):
    """Basic health check endpoint"""
    try:
        # Test database connectivity
        result = await db_manager.fetch_one("SELECT 1 as test")
        db_healthy = result is not None
        
        return {
            "status": "healthy" if db_healthy else "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "components": {
                "database": "healthy" if db_healthy else "unhealthy",
                "api": "healthy"
            }
        }
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        raise HTTPException(status_code=503, detail="Service unhealthy")


@health_router.get("/health/detailed")
async def detailed_health_check(db_manager=Depends(get_db_connection)):
    """Detailed health check with system statistics"""
    try:
        # Database connectivity
        db_test = await db_manager.fetch_one("SELECT 1 as test")
        db_healthy = db_test is not None
        
        # Get database statistics
        stats = {}
        if db_healthy:
            job_count = await db_manager.fetch_one("SELECT COUNT(*) as count FROM jobs")
            task_count = await db_manager.fetch_one("SELECT COUNT(*) as count FROM tasks")
            pending_tasks = await db_manager.fetch_one(
                "SELECT COUNT(*) as count FROM tasks WHERE status = 'PENDING'"
            )
            
            stats = {
                "total_jobs": job_count["count"] if job_count else 0,
                "total_tasks": task_count["count"] if task_count else 0,
                "pending_tasks": pending_tasks["count"] if pending_tasks else 0
            }
        
        return {
            "status": "healthy" if db_healthy else "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "components": {
                "database": "healthy" if db_healthy else "unhealthy",
                "api": "healthy"
            },
            "statistics": stats
        }
    except Exception as e:
        logger.error("Detailed health check failed", error=str(e))
        raise HTTPException(status_code=503, detail="Service unhealthy")