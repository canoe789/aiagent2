"""
FastAPI main application for Project HELIX v2.0
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import structlog
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from src.database.connection import get_global_db_manager, get_db_connection
from src.database.models import JobCreate, JobResponse, Job, Task
from src.api.jobs import jobs_router
from src.api.health import health_router
from src.api.artifacts import artifacts_router
from src.api.auth import get_current_user, optional_auth

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
    await get_global_db_manager().connect()
    logger.info("Database connection established")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Project HELIX API server")
    await get_global_db_manager().disconnect()
    logger.info("Database connection closed")


# Create FastAPI application
app = FastAPI(
    title="Project HELIX API",
    description="AI-driven automated creative production system",
    version="2.0.0",
    lifespan=lifespan
)

# Add CORS middleware with secure defaults
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8000").split(",")
if os.getenv("HELIX_ENV") == "development":
    allowed_origins.append("http://localhost:*")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,  # Secure: only allow specified origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],  # Explicit methods only
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router, prefix="/api/v1")
app.include_router(jobs_router, prefix="/api/v1")
app.include_router(artifacts_router, prefix="/api/v1")

@app.get("/api")
async def api_root(user: dict = Depends(optional_auth)):
    """API root endpoint"""
    response = {
        "message": "Project HELIX API v2.0",
        "description": "AI-driven automated creative production system",
        "docs": "/docs",
        "health": "/api/v1/health",
        "frontend": "/",
        "version": "2.0.0",
        "authentication": "API Key required for protected endpoints"
    }
    
    if user:
        response["authenticated_user"] = {
            "user_id": user["user_id"],
            "role": user["role"]
        }
    
    return response

# 挂载静态文件（前端）- 放在最后以避免覆盖API路由
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "frontend")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="static")


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