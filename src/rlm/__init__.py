"""
RLM - Recursive Language Model
True recursive reasoning implementation using local Qwen2.5-Coder 14B
"""

from .client import OllamaClient
from .controller import RLMController

__all__ = ["OllamaClient", "RLMController"]
