"""Google Gemini adapter for LLM provider port."""

import httpx
import logging
from typing import List

from core_api.domain.ports.llm_port import LLMProviderPort, Message, ChatResponse

logger = logging.getLogger(__name__)

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"


class GeminiAdapter(LLMProviderPort):
    """Google Gemini API adapter."""

    def __init__(self, api_key: str):
        """Initialize the Gemini adapter.

        Args:
            api_key: Google AI API key
        """
        self._api_key = api_key
        self._client = httpx.Client(timeout=120.0)

    def chat(
        self,
        messages: List[Message],
        system_prompt: str,
        max_tokens: int = 2048
    ) -> ChatResponse:
        """Send a chat request to Gemini.

        Args:
            messages: List of conversation messages
            system_prompt: System prompt for the model
            max_tokens: Maximum tokens in response

        Returns:
            ChatResponse with Gemini's reply

        Raises:
            Exception: If API request fails
        """
        if not self._api_key:
            raise ValueError("Gemini API key not configured")

        # Build contents with system instruction
        contents = []

        # Add system prompt as first user message context
        if system_prompt:
            contents.append({
                "role": "user",
                "parts": [{"text": f"[System Instruction]\n{system_prompt}\n[End System Instruction]"}]
            })
            contents.append({
                "role": "model",
                "parts": [{"text": "I understand. I will follow these instructions."}]
            })

        # Add conversation messages
        for msg in messages:
            role = "model" if msg.role == "assistant" else "user"
            contents.append({
                "role": role,
                "parts": [{"text": msg.content}]
            })

        response = self._client.post(
            f"{GEMINI_API_URL}?key={self._api_key}",
            headers={"Content-Type": "application/json"},
            json={
                "contents": contents,
                "generationConfig": {
                    "maxOutputTokens": max_tokens
                }
            }
        )

        if response.status_code == 401 or response.status_code == 403:
            raise ValueError("Invalid Gemini API key")
        elif response.status_code == 429:
            raise ValueError("Rate limit exceeded. Please try again later.")
        elif response.status_code != 200:
            raise ValueError(f"Gemini API error: {response.status_code}")

        result = response.json()
        candidates = result.get("candidates", [])

        if not candidates:
            raise ValueError("Empty response from Gemini")

        content = candidates[0].get("content", {})
        parts = content.get("parts", [])

        if not parts:
            raise ValueError("No content in Gemini response")

        text_content = parts[0].get("text", "")

        return ChatResponse(
            content=text_content,
            model="gemini-pro",
            usage=result.get("usageMetadata")
        )

    def get_provider_name(self) -> str:
        """Get the provider name."""
        return "gemini"

    def is_configured(self) -> bool:
        """Check if configured."""
        return bool(self._api_key)

    def close(self):
        """Close the HTTP client."""
        self._client.close()
