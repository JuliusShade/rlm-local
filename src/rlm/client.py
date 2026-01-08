"""
Ollama API Client
Clean wrapper for OpenAI-compatible API endpoint
"""

import requests
from typing import List, Dict, Any, Optional
import time


class OllamaClient:
    """
    Clean wrapper for Ollama OpenAI-compatible API.
    Handles retries, error handling, and response parsing.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:11434/v1",
        model: str = "qwen2.5-coder:14b",
        timeout: int = 120,
        max_retries: int = 3,
    ):
        """
        Initialize Ollama client.

        Args:
            base_url: Base URL for Ollama API
            model: Model name to use
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
        """
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout
        self.max_retries = max_retries

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs
    ) -> str:
        """
        Send chat completion request.

        Args:
            messages: List of {role, content} dicts
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Max response length
            **kwargs: Additional parameters to pass to API

        Returns:
            Response content as string

        Raises:
            ConnectionError: If Ollama is not reachable
            ValueError: If response format is invalid
        """
        url = f"{self.base_url}/chat/completions"

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs
        }

        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    url,
                    json=payload,
                    timeout=self.timeout
                )
                response.raise_for_status()

                data = response.json()

                # Extract content from OpenAI-compatible format
                if "choices" in data and len(data["choices"]) > 0:
                    content = data["choices"][0]["message"]["content"]
                    return content
                else:
                    raise ValueError(f"Unexpected response format: {data}")

            except requests.exceptions.ConnectionError as e:
                if attempt == self.max_retries - 1:
                    raise ConnectionError(
                        f"Cannot connect to Ollama at {self.base_url}. "
                        f"Make sure Ollama is running. Error: {e}"
                    )
                time.sleep(1)  # Brief pause before retry

            except requests.exceptions.Timeout as e:
                if attempt == self.max_retries - 1:
                    raise TimeoutError(
                        f"Request timed out after {self.timeout}s. "
                        f"Consider increasing timeout or using a smaller model."
                    )
                time.sleep(1)

            except requests.exceptions.HTTPError as e:
                # Don't retry on HTTP errors (4xx, 5xx)
                raise ValueError(f"HTTP error from Ollama: {e}")

        raise RuntimeError("Max retries exceeded")

    def validate_connection(self) -> bool:
        """
        Test if Ollama is reachable and model is available.

        Returns:
            True if connection is successful

        Raises:
            ConnectionError: If Ollama is not reachable
        """
        try:
            # Simple test message
            response = self.chat_completion(
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10
            )
            return True
        except Exception as e:
            raise ConnectionError(
                f"Failed to validate Ollama connection: {e}"
            )

    def __repr__(self) -> str:
        return f"OllamaClient(model={self.model}, base_url={self.base_url})"
