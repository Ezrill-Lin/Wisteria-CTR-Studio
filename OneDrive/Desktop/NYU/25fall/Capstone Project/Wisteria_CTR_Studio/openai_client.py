"""OpenAI client implementation for LLM click prediction."""

import os
from typing import Any, Dict, List

from base_client import BaseLLMClient




class OpenAIClient(BaseLLMClient):
    """OpenAI client for click prediction."""
    
    def __init__(self, model: str = "gpt-4o-mini", api_key: str = None):
        """Initialize OpenAI client.
        
        Args:
            model: Model name to use.
            api_key: API key override (else read from OPENAI_API_KEY env var).
        """
        super().__init__(model, api_key)
        self.provider_name = "openai"
        self.env_key_name = "OPENAI_API_KEY"
    


    def _get_client(self):
        """Get synchronous OpenAI client."""
        try:
            from openai import OpenAI
            return OpenAI(api_key=self.api_key or os.getenv(self.env_key_name))
        except Exception as e:
            raise ImportError(f"OpenAI import failed: {e}")
    
    async def _get_async_client(self):
        """Get asynchronous OpenAI client."""
        try:
            from openai import AsyncOpenAI
            return AsyncOpenAI(api_key=self.api_key or os.getenv(self.env_key_name))
        except Exception as e:
            raise ImportError(f"AsyncOpenAI import failed: {e}")
    


    def _create_messages(self, prompt: str) -> List[Dict[str, str]]:
        """Create message format for OpenAI API."""
        return [
            {"role": "system", "content": "You are a precise decision engine that outputs strict JSON."},
            {"role": "user", "content": prompt}
        ]
    


    def predict_chunk(self, ad_text: str, chunk: List[Dict[str, Any]], ad_platform: str = "facebook") -> List[int]:
        """Synchronous prediction for a chunk of profiles."""
        try:
            client = self._get_client()
        except ImportError:
            return self._fallback_to_mock(ad_text, chunk, "OpenAI import failed")
        except Exception:
            return self._fallback_to_mock(ad_text, chunk, "OpenAI client init failed")
        
        prompt = self._build_prompt(ad_text, chunk, ad_platform)
        try:
            resp = client.chat.completions.create(
                model=self.model,
                messages=self._create_messages(prompt),
                temperature=0.0,
            )
            content = resp.choices[0].message.content
        except Exception:
            # Try responses API as fallback
            try:
                r = client.responses.create(
                    model=self.model,
                    input=prompt,
                )
                content = r.output_text
            except Exception:
                return self._fallback_to_mock(ad_text, chunk, "OpenAI API call failed")
        
        return self._parse_and_validate_response(content, chunk, ad_text, "OpenAI")
    
    async def predict_chunk_async(self, ad_text: str, chunk: List[Dict[str, Any]], ad_platform: str = "facebook") -> List[int]:
        """Asynchronous prediction for a chunk of profiles."""
        try:
            client = await self._get_async_client()
        except ImportError:
            return self._fallback_to_mock(ad_text, chunk, "AsyncOpenAI import failed")
        except Exception:
            return self._fallback_to_mock(ad_text, chunk, "AsyncOpenAI client init failed")
        
        prompt = self._build_prompt(ad_text, chunk, ad_platform)
        try:
            resp = await client.chat.completions.create(
                model=self.model,
                messages=self._create_messages(prompt),
                temperature=0.0,
            )
            content = resp.choices[0].message.content
        except Exception:
            return self._fallback_to_mock(ad_text, chunk, "AsyncOpenAI API call failed")
        
        return self._parse_and_validate_response(content, chunk, ad_text, "AsyncOpenAI")