"""Anthropic Claude adapter for LLM provider port."""

import httpx
import logging
from typing import List

from core_api.domain.ports.llm_port import LLMProviderPort, Message, ChatResponse

logger = logging.getLogger(__name__)

ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"


class AnthropicAdapter(LLMProviderPort):
    """Anthropic Claude API adapter."""

    def __init__(self, api_key: str):
        """Initialize the Anthropic adapter.

        Args:
            api_key: Anthropic API key
        """
        self._api_key = api_key
        self._client = httpx.Client(timeout=120.0)

    def chat(
        self,
        messages: List[Message],
        system_prompt: str,
        max_tokens: int = 2048
    ) -> ChatResponse:
        """Send a chat request to Claude.

        Args:
            messages: List of conversation messages
            system_prompt: System prompt for the model
            max_tokens: Maximum tokens in response

        Returns:
            ChatResponse with Claude's reply

        Raises:
            Exception: If API request fails
        """
        if not self._api_key:
            raise ValueError("Anthropic API key not configured")

        # Convert messages to Anthropic format
        api_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

        response = self._client.post(
            ANTHROPIC_API_URL,
            headers={
                "x-api-key": self._api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            },
            json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": max_tokens,
                "system": system_prompt,
                "messages": api_messages
            }
        )

        if response.status_code == 401:
            raise ValueError("Invalid Anthropic API key")
        elif response.status_code == 429:
            raise ValueError("Rate limit exceeded. Please try again later.")
        elif response.status_code != 200:
            raise ValueError(f"Anthropic API error: {response.status_code}")

        result = response.json()
        content = result.get("content", [])

        if not content:
            raise ValueError("Empty response from Anthropic")

        text_content = content[0].get("text", "")

        return ChatResponse(
            content=text_content,
            model=result.get("model", "claude-sonnet-4-20250514"),
            usage=result.get("usage")
        )

    def get_provider_name(self) -> str:
        """Get the provider name."""
        return "anthropic"

    def is_configured(self) -> bool:
        """Check if configured."""
        return bool(self._api_key)

    def close(self):
        """Close the HTTP client."""
        self._client.close()
