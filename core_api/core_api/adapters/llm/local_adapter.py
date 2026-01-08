"""Local LLM adapter for LLM provider port (Ollama, LM Studio, etc.)."""

import httpx
import logging
from typing import List

from core_api.domain.ports.llm_port import LLMProviderPort, Message, ChatResponse

logger = logging.getLogger(__name__)


class LocalAdapter(LLMProviderPort):
    """Local LLM API adapter (compatible with Ollama API format)."""

    def __init__(self, endpoint: str, model: str = "llama2"):
        """Initialize the local adapter.

        Args:
            endpoint: Local API endpoint (e.g., http://localhost:11434)
            model: Model name to use
        """
        self._endpoint = endpoint.rstrip('/')
        self._model = model
        self._client = httpx.Client(timeout=120.0)

    def chat(
        self,
        messages: List[Message],
        system_prompt: str,
        max_tokens: int = 2048
    ) -> ChatResponse:
        """Send a chat request to the local LLM.

        Args:
            messages: List of conversation messages
            system_prompt: System prompt for the model
            max_tokens: Maximum tokens in response

        Returns:
            ChatResponse with the model's reply

        Raises:
            Exception: If API request fails
        """
        if not self._endpoint:
            raise ValueError("Local LLM endpoint not configured")

        # Build messages with system prompt (Ollama format)
        api_messages = []
        if system_prompt:
            api_messages.append({"role": "system", "content": system_prompt})

        api_messages.extend([
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ])

        try:
            response = self._client.post(
                f"{self._endpoint}/api/chat",
                json={
                    "model": self._model,
                    "messages": api_messages,
                    "stream": False,
                    "options": {
                        "num_predict": max_tokens
                    }
                }
            )
        except httpx.ConnectError:
            raise ValueError(f"Cannot connect to local LLM at {self._endpoint}")

        if response.status_code != 200:
            raise ValueError(f"Local LLM API error: {response.status_code}")

        result = response.json()
        message = result.get("message", {})
        text_content = message.get("content", "")

        if not text_content:
            raise ValueError("Empty response from local LLM")

        return ChatResponse(
            content=text_content,
            model=self._model,
            usage=None
        )

    def get_provider_name(self) -> str:
        """Get the provider name."""
        return "local"

    def is_configured(self) -> bool:
        """Check if configured."""
        return bool(self._endpoint)

    def close(self):
        """Close the HTTP client."""
        self._client.close()
