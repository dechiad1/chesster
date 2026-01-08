"""OpenAI GPT adapter for LLM provider port."""

import httpx
import logging
from typing import List

from core_api.domain.ports.llm_port import LLMProviderPort, Message, ChatResponse

logger = logging.getLogger(__name__)

OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"


class OpenAIAdapter(LLMProviderPort):
    """OpenAI GPT API adapter."""

    def __init__(self, api_key: str):
        """Initialize the OpenAI adapter.

        Args:
            api_key: OpenAI API key
        """
        self._api_key = api_key
        self._client = httpx.Client(timeout=120.0)

    def chat(
        self,
        messages: List[Message],
        system_prompt: str,
        max_tokens: int = 2048
    ) -> ChatResponse:
        """Send a chat request to GPT.

        Args:
            messages: List of conversation messages
            system_prompt: System prompt for the model
            max_tokens: Maximum tokens in response

        Returns:
            ChatResponse with GPT's reply

        Raises:
            Exception: If API request fails
        """
        if not self._api_key:
            raise ValueError("OpenAI API key not configured")

        # Build messages with system prompt
        api_messages = [{"role": "system", "content": system_prompt}]
        api_messages.extend([
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ])

        response = self._client.post(
            OPENAI_API_URL,
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-4o",
                "max_tokens": max_tokens,
                "messages": api_messages
            }
        )

        if response.status_code == 401:
            raise ValueError("Invalid OpenAI API key")
        elif response.status_code == 429:
            raise ValueError("Rate limit exceeded. Please try again later.")
        elif response.status_code != 200:
            raise ValueError(f"OpenAI API error: {response.status_code}")

        result = response.json()
        choices = result.get("choices", [])

        if not choices:
            raise ValueError("Empty response from OpenAI")

        text_content = choices[0].get("message", {}).get("content", "")

        return ChatResponse(
            content=text_content,
            model=result.get("model", "gpt-4o"),
            usage=result.get("usage")
        )

    def get_provider_name(self) -> str:
        """Get the provider name."""
        return "openai"

    def is_configured(self) -> bool:
        """Check if configured."""
        return bool(self._api_key)

    def close(self):
        """Close the HTTP client."""
        self._client.close()
