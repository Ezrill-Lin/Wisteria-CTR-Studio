"""CTRPrediction (Click-Through Rate Prediction) Package

This package provides specialized tools for CTR (Click-Through Rate) prediction
using synthetic populations and LLM-based models. It includes multiple LLM 
provider clients and core prediction functionality for advertising effectiveness analysis.

Main Components:
- llm_click_model: Core LLM-based click prediction functionality
- Client modules: Various LLM provider clients (OpenAI, DeepSeek, etc.)
- base_client: Abstract base class for LLM client implementations
"""

from .llm_click_model import LLMClickPredictor
from .base_client import BaseLLMClient

__version__ = "1.0.0"
__all__ = ["LLMClickPredictor", "BaseLLMClient"]