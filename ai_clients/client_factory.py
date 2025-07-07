"""
AI Client Factory for Project HELIX v2.0
Manages creation and configuration of AI clients
"""

import os
from typing import Dict, Any, Optional
import structlog

from .base_client import BaseAIClient, AIModelError
from .deepseek_client import DeepSeekClient
from .gemini_client import GeminiClient

logger = structlog.get_logger(__name__)


class AIClientFactory:
    """
    Factory for creating and managing AI clients
    Handles provider selection and configuration
    """
    
    # Registry of available providers
    PROVIDERS = {
        "deepseek": DeepSeekClient,
        "gemini": GeminiClient,
    }
    
    # Default models for each provider
    DEFAULT_MODELS = {
        "deepseek": "deepseek-chat",
        "gemini": "gemini-1.5-flash",
    }
    
    # Environment variable mapping
    API_KEY_MAPPING = {
        "deepseek": "DEEPSEEK_API_KEY",
        "gemini": "GEMINI_API_KEY",
    }
    
    @classmethod
    def create_client(
        cls, 
        provider: str = None, 
        model: str = None,
        api_key: str = None,
        **kwargs
    ) -> BaseAIClient:
        """
        Create an AI client instance
        
        Args:
            provider: AI provider name (deepseek, gemini)
            model: Specific model name (optional)
            api_key: API key (optional, will use env var if not provided)
            **kwargs: Additional configuration parameters
            
        Returns:
            BaseAIClient: Configured AI client instance
            
        Raises:
            AIModelError: If provider is not supported or configuration is invalid
        """
        
        # Use default provider if not specified
        if not provider:
            provider = os.getenv("DEFAULT_AI_PROVIDER", "deepseek")
        
        # Validate provider
        if provider not in cls.PROVIDERS:
            available = ", ".join(cls.PROVIDERS.keys())
            raise AIModelError(f"Unsupported provider '{provider}'. Available: {available}")
        
        # Get API key
        if not api_key:
            env_var = cls.API_KEY_MAPPING.get(provider)
            if env_var:
                api_key = os.getenv(env_var)
            
            if not api_key:
                raise AIModelError(f"API key not found for {provider}. Set {env_var} environment variable.")
        
        # Use default model if not specified
        if not model:
            model = cls.DEFAULT_MODELS.get(provider)
        
        # Get client class and create instance
        client_class = cls.PROVIDERS[provider]
        
        try:
            client = client_class(api_key=api_key, model_name=model, **kwargs)
            
            logger.info("AI client created successfully", 
                       provider=provider, 
                       model=model)
            
            return client
            
        except Exception as e:
            logger.error("Failed to create AI client", 
                        provider=provider, 
                        model=model, 
                        error=str(e))
            raise AIModelError(f"Failed to create {provider} client: {str(e)}")
    
    @classmethod
    def get_available_providers(cls) -> Dict[str, Dict[str, Any]]:
        """
        Get information about available providers
        
        Returns:
            Dict with provider info including models and status
        """
        providers_info = {}
        
        for provider, client_class in cls.PROVIDERS.items():
            api_key_env = cls.API_KEY_MAPPING.get(provider)
            api_key_configured = bool(os.getenv(api_key_env))
            
            providers_info[provider] = {
                "client_class": client_class.__name__,
                "default_model": cls.DEFAULT_MODELS.get(provider),
                "api_key_env_var": api_key_env,
                "api_key_configured": api_key_configured,
                "description": cls._get_provider_description(provider)
            }
        
        return providers_info
    
    @classmethod
    def _get_provider_description(cls, provider: str) -> str:
        """Get description for a provider"""
        descriptions = {
            "deepseek": "DeepSeek AI - High-quality conversational AI with strong reasoning capabilities",
            "gemini": "Google Gemini Flash - Fast and efficient multimodal AI model",
        }
        return descriptions.get(provider, f"{provider.title()} AI provider")
    
    @classmethod
    async def validate_all_providers(cls) -> Dict[str, bool]:
        """
        Validate API keys for all configured providers
        
        Returns:
            Dict mapping provider names to validation status
        """
        validation_results = {}
        
        for provider in cls.PROVIDERS.keys():
            try:
                client = cls.create_client(provider=provider)
                is_valid = await client.validate_api_key()
                validation_results[provider] = is_valid
                
                logger.info("Provider validation completed", 
                           provider=provider, 
                           valid=is_valid)
                
            except Exception as e:
                validation_results[provider] = False
                logger.warning("Provider validation failed", 
                              provider=provider, 
                              error=str(e))
        
        return validation_results


class AIClientManager:
    """
    Singleton manager for AI clients with caching and configuration
    """
    
    _instance = None
    _clients = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def get_client(self, provider: str = None, **kwargs) -> BaseAIClient:
        """
        Get or create a cached AI client
        
        Args:
            provider: AI provider name
            **kwargs: Additional configuration
            
        Returns:
            BaseAIClient: Cached or new client instance
        """
        if not provider:
            provider = os.getenv("DEFAULT_AI_PROVIDER", "deepseek")
        
        cache_key = f"{provider}_{hash(str(sorted(kwargs.items())))}"
        
        if cache_key not in self._clients:
            self._clients[cache_key] = AIClientFactory.create_client(
                provider=provider, 
                **kwargs
            )
        
        return self._clients[cache_key]
    
    def clear_cache(self):
        """Clear the client cache"""
        self._clients.clear()
        logger.info("AI client cache cleared")


# Global manager instance
ai_client_manager = AIClientManager()