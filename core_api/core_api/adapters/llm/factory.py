"""Factory for creating LLM provider instances."""

from typing import Optional

from core_api.domain.ports.llm_port import LLMProviderPort
from core_api.adapters.llm.anthropic_adapter import AnthropicAdapter
from core_api.adapters.llm.openai_adapter import OpenAIAdapter
from core_api.adapters.llm.gemini_adapter import GeminiAdapter
from core_api.adapters.llm.local_adapter import LocalAdapter


def create_llm_provider(
    provider: str,
    api_key: str = "",
    endpoint: str = ""
) -> Optional[LLMProviderPort]:
    """Create an LLM provider instance.

    Args:
        provider: Provider name ('anthropic', 'openai', 'gemini', 'local')
        api_key: API key for the provider (not needed for local)
        endpoint: Endpoint URL (only for local provider)

    Returns:
        LLMProviderPort instance or None if invalid provider
    """
    provider = provider.lower()

    if provider == "anthropic":
        return AnthropicAdapter(api_key)
    elif provider == "openai":
        return OpenAIAdapter(api_key)
    elif provider == "gemini":
        return GeminiAdapter(api_key)
    elif provider == "local":
        return LocalAdapter(endpoint or "http://localhost:11434")
    else:
        return None
