"""DeepSeek client implementation for LLM click prediction."""

import os
from typing import Any, Dict, List

from .base_client import BaseLLMClient


class DeepSeekClient(BaseLLMClient):
    """DeepSeek client for click prediction."""
    
    def __init__(self, model: str = "deepseek-chat", api_key: str = None):
        """Initialize DeepSeek client.
        
        Args:
            model: Model name to use.
            api_key: API key override (else read from DEEPSEEK_API_KEY env var).
        """
        super().__init__(model, api_key)
        self.provider_name = "deepseek"
        self.env_key_name = "DEEPSEEK_API_KEY"
        self.base_url = os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com")
    


    def _get_client(self):
        """Get synchronous OpenAI client configured for DeepSeek."""
        try:
            from openai import OpenAI
            return OpenAI(
                api_key=self.api_key or os.getenv(self.env_key_name),
                base_url=self.base_url
            )
        except Exception as e:
            raise ImportError(f"OpenAI import failed: {e}")

    async def _get_async_client(self):
        """Get asynchronous OpenAI client configured for DeepSeek."""
        try:
            from openai import AsyncOpenAI
            return AsyncOpenAI(
                api_key=self.api_key or os.getenv(self.env_key_name),
                base_url=self.base_url
            )
        except Exception as e:
            raise ImportError(f"AsyncOpenAI import failed: {e}")
    


    def _create_messages(self, prompt: str) -> List[Dict[str, str]]:
        """Create message format for DeepSeek API."""
        return [
            {"role": "system", "content": "You are a precise decision engine that outputs strict JSON."},
            {"role": "user", "content": prompt}
        ]
    


    def predict_chunk(self, ad_text: str, chunk: List[Dict[str, Any]], ad_platform: str = "facebook") -> List[int]:
        """Synchronous prediction for a chunk of profiles."""
        # Check API key first
        if not self.has_api_key():
            return self._fallback_to_mock(ad_text, chunk, "DeepSeek API key missing")
        
        try:
            client = self._get_client()
        except ImportError:
            return self._fallback_to_mock(ad_text, chunk, "OpenAI import failed")
        except Exception:
            return self._fallback_to_mock(ad_text, chunk, "DeepSeek client init failed")
        
        prompt = self._build_prompt(ad_text, chunk, ad_platform)
        try:
            response = client.chat.completions.create(
                model=self.model or "deepseek-chat",
                messages=self._create_messages(prompt),
                temperature=0.0,
                stream=False
            )
            content = response.choices[0].message.content
        except Exception:
            return self._fallback_to_mock(ad_text, chunk, "DeepSeek API call failed")
        
        return self._parse_and_validate_response(content, chunk, ad_text, "DeepSeek")

    async def predict_chunk_async(self, ad_text: str, chunk: List[Dict[str, Any]], ad_platform: str = "facebook") -> List[int]:
        """Asynchronous prediction for a chunk of profiles."""
        # Check API key first
        if not self.has_api_key():
            return self._fallback_to_mock(ad_text, chunk, "DeepSeek API key missing")
        
        try:
            client = await self._get_async_client()
        except ImportError:
            return self._fallback_to_mock(ad_text, chunk, "AsyncOpenAI import failed")
        except Exception:
            return self._fallback_to_mock(ad_text, chunk, "AsyncDeepSeek client init failed")
        
        prompt = self._build_prompt(ad_text, chunk, ad_platform)
        try:
            response = await client.chat.completions.create(
                model=self.model or "deepseek-chat",
                messages=self._create_messages(prompt),
                temperature=0.0,
                stream=False
            )
            content = response.choices[0].message.content
        except Exception:
            return self._fallback_to_mock(ad_text, chunk, "AsyncDeepSeek API call failed")
        
        return self._parse_and_validate_response(content, chunk, ad_text, "AsyncDeepSeek")