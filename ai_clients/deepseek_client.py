"""
DeepSeek AI Client for Project HELIX v2.0
Implements DeepSeek API integration
"""

import asyncio
import aiohttp
import json
from typing import Dict, Any, Optional
import structlog

from .base_client import BaseAIClient, AIModelError, RateLimitError, InvalidAPIKeyError

logger = structlog.get_logger(__name__)


class DeepSeekClient(BaseAIClient):
    """
    DeepSeek AI client implementation
    Uses DeepSeek's chat completion API
    """
    
    def __init__(self, api_key: str, model_name: str = "deepseek-chat", **kwargs):
        super().__init__(api_key, model_name, **kwargs)
        self.base_url = "https://api.deepseek.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
    async def generate_response(
        self, 
        system_prompt: str, 
        user_input: str, 
        temperature: float = 0.7,
        max_tokens: int = 4000,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate response using DeepSeek API
        """
        try:
            # Prepare request payload
            payload = {
                "model": self.model_name,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": False
            }
            
            # Add any additional parameters
            payload.update(kwargs)
            
            logger.info("Making DeepSeek API request", 
                       model=self.model_name, 
                       temperature=temperature,
                       max_tokens=max_tokens)
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=120)  # 增加到2分钟
                ) as response:
                    
                    response_data = await response.json()
                    
                    if response.status == 401:
                        raise InvalidAPIKeyError("Invalid DeepSeek API key", "deepseek")
                    elif response.status == 429:
                        raise RateLimitError("DeepSeek API rate limit exceeded", "deepseek")
                    elif response.status != 200:
                        error_msg = response_data.get("error", {}).get("message", "Unknown error")
                        raise AIModelError(f"DeepSeek API error: {error_msg}", "deepseek", str(response.status))
                    
                    # Extract response content
                    if "choices" not in response_data or not response_data["choices"]:
                        raise AIModelError("No response choices returned", "deepseek")
                    
                    choice = response_data["choices"][0]
                    content = choice["message"]["content"]
                    
                    # Prepare response
                    result = {
                        "content": content,
                        "provider": "deepseek",
                        "model": response_data.get("model", self.model_name),
                        "usage": response_data.get("usage", {}),
                        "finish_reason": choice.get("finish_reason"),
                        "raw_response": response_data
                    }
                    
                    logger.info("DeepSeek response received successfully",
                               content_length=len(content),
                               tokens_used=result["usage"].get("total_tokens", 0))
                    
                    return result
                    
        except aiohttp.ClientError as e:
            logger.error("DeepSeek API connection error", error=str(e))
            raise AIModelError(f"Connection error: {str(e)}", "deepseek")
        except asyncio.TimeoutError:
            logger.error("DeepSeek API timeout")
            raise AIModelError("Request timeout", "deepseek")
        except Exception as e:
            if isinstance(e, (AIModelError, RateLimitError, InvalidAPIKeyError)):
                raise
            logger.error("Unexpected DeepSeek API error", error=str(e))
            raise AIModelError(f"Unexpected error: {str(e)}", "deepseek")
    
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
async def test_deepseek_client():
    """Test function for DeepSeek client"""
    import os
    
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key or api_key == "your_deepseek_api_key_here":
        print("❌ DeepSeek API key not configured")
        return False
    
    client = DeepSeekClient(api_key)
    
    try:
        # Test API key validation
        print("🔍 Validating DeepSeek API key...")
        is_valid = await client.validate_api_key()
        
        if not is_valid:
            print("❌ DeepSeek API key validation failed")
            return False
        
        print("✅ DeepSeek API key is valid")
        
        # Test generation
        print("🤖 Testing DeepSeek generation...")
        response = await client.generate_response(
            system_prompt="You are a creative director. Respond with a brief, structured analysis.",
            user_input="Analyze the concept of a modern coffee shop website",
            temperature=0.7,
            max_tokens=200
        )
        
        print(f"✅ DeepSeek response received ({len(response['content'])} chars)")
        print(f"📊 Usage: {response['usage']}")
        
        return True
        
    except Exception as e:
        print(f"❌ DeepSeek test failed: {e}")
        return False


if __name__ == "__main__":
    asyncio.run(test_deepseek_client())