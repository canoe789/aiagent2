"""
Base AI Client for Project HELIX v2.0
Abstract interface for different AI providers
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import structlog

logger = structlog.get_logger(__name__)


class BaseAIClient(ABC):
    """
    Abstract base class for AI model clients
    Provides unified interface for different AI providers
    """
    
    def __init__(self, api_key: str, model_name: str = None, **kwargs):
        self.api_key = api_key
        self.model_name = model_name
        self.config = kwargs
        
    @abstractmethod
    async def generate_response(
        self, 
        system_prompt: str, 
        user_input: str, 
        temperature: float = 0.7,
        max_tokens: int = 4000,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate AI response
        
        Args:
            system_prompt: System/instruction prompt
            user_input: User's input message
            temperature: Response creativity (0-1)
            max_tokens: Maximum response length
            **kwargs: Provider-specific parameters
            
        Returns:
            Dict containing:
                - content: Generated text content
                - usage: Token usage information
                - model: Model used
                - provider: Provider name
        """
        pass
    
    @abstractmethod
    async def validate_api_key(self) -> bool:
        """Validate API key by making a test request"""
        pass
    
    def get_provider_name(self) -> str:
        """Get provider name"""
        return self.__class__.__name__.replace('Client', '').lower()


class AIModelError(Exception):
    """Custom exception for AI model errors"""
    
    def __init__(self, message: str, provider: str = None, error_code: str = None):
        self.provider = provider
        self.error_code = error_code
        super().__init__(message)


class RateLimitError(AIModelError):
    """Raised when API rate limit is exceeded"""
    pass


class InvalidAPIKeyError(AIModelError):
    """Raised when API key is invalid"""
    pass


class ModelNotFoundError(AIModelError):
    """Raised when requested model is not available"""
    pass