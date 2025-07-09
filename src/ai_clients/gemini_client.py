"""
Google Gemini AI Client for Project HELIX v2.0
Implements Google Gemini Flash API integration
"""

import asyncio
import aiohttp
import json
from typing import Dict, Any, Optional
import structlog

from .base_client import BaseAIClient, AIModelError, RateLimitError, InvalidAPIKeyError

logger = structlog.get_logger(__name__)


class GeminiClient(BaseAIClient):
    """
    Google Gemini AI client implementation
    Uses Gemini Flash for fast, efficient responses
    """
    
    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash", **kwargs):
        super().__init__(api_key, model_name, **kwargs)
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        
    async def generate_response(
        self, 
        system_prompt: str, 
        user_input: str, 
        temperature: float = 0.7,
        max_tokens: int = 4000,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate response using Gemini API
        """
        try:
            # Combine system prompt and user input for Gemini
            combined_prompt = f"{system_prompt}\n\nUser Request: {user_input}"
            
            # Prepare request payload for Gemini format
            payload = {
                "contents": [{
                    "parts": [{
                        "text": combined_prompt
                    }]
                }],
                "generationConfig": {
                    "temperature": temperature,
                    "maxOutputTokens": max_tokens,
                    "topP": kwargs.get("top_p", 0.95),
                    "topK": kwargs.get("top_k", 64)
                }
            }
            
            # Add safety settings if provided
            if "safety_settings" in kwargs:
                payload["safetySettings"] = kwargs["safety_settings"]
            
            url = f"{self.base_url}/models/{self.model_name}:generateContent?key={self.api_key}"
            
            logger.info("Making Gemini API request", 
                       model=self.model_name, 
                       temperature=temperature,
                       max_tokens=max_tokens)
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    
                    response_data = await response.json()
                    
                    if response.status == 400:
                        error_msg = response_data.get("error", {}).get("message", "Bad request")
                        if "API_KEY_INVALID" in error_msg:
                            raise InvalidAPIKeyError("Invalid Gemini API key", "gemini")
                        raise AIModelError(f"Gemini API error: {error_msg}", "gemini", "400")
                    elif response.status == 429:
                        raise RateLimitError("Gemini API rate limit exceeded", "gemini")
                    elif response.status != 200:
                        error_msg = response_data.get("error", {}).get("message", "Unknown error")
                        raise AIModelError(f"Gemini API error: {error_msg}", "gemini", str(response.status))
                    
                    # Extract response content from Gemini format
                    if "candidates" not in response_data or not response_data["candidates"]:
                        raise AIModelError("No candidates returned from Gemini", "gemini")
                    
                    candidate = response_data["candidates"][0]
                    
                    if "content" not in candidate or "parts" not in candidate["content"]:
                        raise AIModelError("Invalid response format from Gemini", "gemini")
                    
                    content = candidate["content"]["parts"][0]["text"]
                    
                    # Extract usage information
                    usage_metadata = response_data.get("usageMetadata", {})
                    usage = {
                        "prompt_tokens": usage_metadata.get("promptTokenCount", 0),
                        "completion_tokens": usage_metadata.get("candidatesTokenCount", 0),
                        "total_tokens": usage_metadata.get("totalTokenCount", 0)
                    }
                    
                    # Prepare response
                    result = {
                        "content": content,
                        "provider": "gemini",
                        "model": self.model_name,
                        "usage": usage,
                        "finish_reason": candidate.get("finishReason", "STOP"),
                        "safety_ratings": candidate.get("safetyRatings", []),
                        "raw_response": response_data
                    }
                    
                    logger.info("Gemini response received successfully",
                               content_length=len(content),
                               tokens_used=usage["total_tokens"])
                    
                    return result
                    
        except aiohttp.ClientError as e:
            logger.error("Gemini API connection error", error=str(e))
            raise AIModelError(f"Connection error: {str(e)}", "gemini")
        except asyncio.TimeoutError:
            logger.error("Gemini API timeout")
            raise AIModelError("Request timeout", "gemini")
        except Exception as e:
            if isinstance(e, (AIModelError, RateLimitError, InvalidAPIKeyError)):
                raise
            logger.error("Unexpected Gemini API error", error=str(e))
            raise AIModelError(f"Unexpected error: {str(e)}", "gemini")
    
    async def validate_api_key(self) -> bool:
        """
        Validate API key by making a simple test request
        """
        try:
            test_response = await self.generate_response(
                system_prompt="You are a helpful assistant.",
                user_input="Hello",
                temperature=0.1,
                max_tokens=10
            )
            return test_response.get("content") is not None
            
        except InvalidAPIKeyError:
            return False
        except Exception as e:
            logger.warning("API key validation failed", error=str(e))
            return False


# Example usage and testing
async def test_gemini_client():
    """Test function for Gemini client"""
    import os
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        print("❌ Gemini API key not configured")
        return False
    
    client = GeminiClient(api_key)
    
    try:
        # Test API key validation
        print("🔍 Validating Gemini API key...")
        is_valid = await client.validate_api_key()
        
        if not is_valid:
            print("❌ Gemini API key validation failed")
            return False
        
        print("✅ Gemini API key is valid")
        
        # Test generation
        print("🤖 Testing Gemini generation...")
        response = await client.generate_response(
            system_prompt="You are a visual director. Respond with a brief, structured analysis.",
            user_input="Design visual concepts for a modern coffee shop website",
            temperature=0.7,
            max_tokens=200
        )
        
        print(f"✅ Gemini response received ({len(response['content'])} chars)")
        print(f"📊 Usage: {response['usage']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Gemini test failed: {e}")
        return False


if __name__ == "__main__":
    asyncio.run(test_gemini_client())