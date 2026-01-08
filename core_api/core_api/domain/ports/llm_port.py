"""LLM provider port interface."""

from abc import ABC, abstractmethod
from typing import List, Optional, AsyncIterator
from pydantic import BaseModel


class Message(BaseModel):
    """Chat message model."""
    role: str  # 'user', 'assistant', 'system'
    content: str


class ChatResponse(BaseModel):
    """Chat response model."""
    content: str
    model: str
    usage: Optional[dict] = None


class LLMProviderPort(ABC):
    """Abstract interface for LLM providers.

    Implementations must handle their own API authentication
    and request formatting.
    """

    @abstractmethod
    def chat(
        self,
        messages: List[Message],
        system_prompt: str,
        max_tokens: int = 2048
    ) -> ChatResponse:
        """Send a chat request to the LLM.

        Args:
            messages: List of conversation messages
            system_prompt: System prompt for the model
            max_tokens: Maximum tokens in response

        Returns:
            ChatResponse with the model's reply
        """
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """Get the name of this provider.

        Returns:
            Provider name string
        """
        pass

    @abstractmethod
    def is_configured(self) -> bool:
        """Check if the provider is properly configured.

        Returns:
            True if API key/endpoint is set
        """
        pass
