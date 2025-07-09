"""
Authentication middleware for Project HELIX v2.0
Simple API Key based authentication system
"""

from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
import structlog
from typing import Optional

logger = structlog.get_logger(__name__)

# Initialize HTTP Bearer security scheme
security = HTTPBearer(auto_error=False)

# Get API keys from environment
API_KEYS = set(filter(None, [
    os.getenv("HELIX_API_KEY"),
    os.getenv("HELIX_ADMIN_API_KEY"),
    os.getenv("HELIX_DEV_API_KEY")
]))

# If no API keys are configured, use a default one for development
if not API_KEYS:
    logger.warning("No API keys configured, using development default - authentication disabled")
    # NOTE: In production, this should raise an error instead
    # For development, we allow unauthenticated access
    pass

async def verify_api_key(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> str:
    """
    Verify API key from Authorization header
    
    Returns:
        str: The verified API key
        
    Raises:
        HTTPException: If authentication fails
    """
    # If no API keys configured and in development, allow access
    if not API_KEYS and os.getenv("HELIX_ENV", "development") == "development":
        logger.debug("Development mode - authentication bypassed")
        return "development-bypass"
    
    if not credentials:
        logger.warning("Missing authorization header")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if credentials.credentials not in API_KEYS:
        logger.warning("Invalid API key attempted", api_key_prefix=credentials.credentials[:8] + "...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    logger.info("API key authenticated successfully", api_key_prefix=credentials.credentials[:8] + "...")
    return credentials.credentials

async def get_current_user(api_key: str = Depends(verify_api_key)) -> dict:
    """
    Get current user information based on API key
    
    Args:
        api_key: The verified API key
        
    Returns:
        dict: User information
    """
    # In a real system, this would look up user info from database
    # For now, return basic info based on API key type
    if api_key == "development-bypass":
        return {"user_id": "dev", "role": "developer", "permissions": ["read", "write"]}
    
    if api_key == os.getenv("HELIX_ADMIN_API_KEY"):
        return {"user_id": "admin", "role": "admin", "permissions": ["read", "write", "admin"]}
    
    return {"user_id": "user", "role": "user", "permissions": ["read", "write"]}

# Optional dependency for endpoints that don't require authentication
async def optional_auth(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[dict]:
    """
    Optional authentication - doesn't raise exception if no auth provided
    
    Returns:
        Optional[dict]: User info if authenticated, None if not
    """
    if not credentials:
        return None
    
    try:
        api_key = await verify_api_key(credentials)
        return await get_current_user(api_key)
    except HTTPException:
        return None