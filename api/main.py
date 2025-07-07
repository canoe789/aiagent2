"""
FastAPI main application for Project HELIX v2.0
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import structlog
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from database.connection import db_manager, get_db_connection
from database.models import JobCreate, JobResponse, Job, Task
from api.jobs import jobs_router
from api.health import health_router

# Configure structured logging
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

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting Project HELIX API server")
    await db_manager.connect()
    logger.info("Database connection established")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Project HELIX API server")
    await db_manager.disconnect()
    logger.info("Database connection closed")


# Create FastAPI application
app = FastAPI(
    title="Project HELIX API",
    description="AI-driven automated creative production system",
    version="2.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router, prefix="/api/v1")
app.include_router(jobs_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Project HELIX API v2.0",
        "description": "AI-driven automated creative production system",
        "docs": "/docs",
        "health": "/api/v1/health"
    }


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("API_PORT", 8000))
    host = os.getenv("API_HOST", "0.0.0.0")
    
    uvicorn.run(
        "api.main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )