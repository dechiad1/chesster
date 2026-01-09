"""Local configuration service for the desktop client."""

import json
import logging
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class LLMConfig(BaseModel):
    """LLM provider configuration."""
    provider: str = Field(default="anthropic", description="LLM provider: anthropic, openai, gemini, local")
    anthropic_api_key: str = ""
    openai_api_key: str = ""
    gemini_api_key: str = ""
    local_endpoint: str = "http://localhost:11434"


class AppConfig(BaseModel):
    """Application configuration stored locally."""
    llm: LLMConfig = Field(default_factory=LLMConfig)
    chesscom_username: str = ""
    account_user_id: Optional[int] = None

    # UI preferences
    board_theme: str = "classic"
    show_coordinates: bool = True
    auto_save_games: bool = True


class ConfigService:
    """Service for managing local application configuration."""

    DEFAULT_CONFIG_DIR = Path.home() / ".chesster"
    DEFAULT_CONFIG_FILE = "config.json"

    def __init__(self, config_dir: Optional[Path] = None):
        """Initialize the config service.

        Args:
            config_dir: Optional custom config directory path
        """
        self.config_dir = config_dir or self.DEFAULT_CONFIG_DIR
        self.config_file = self.config_dir / self.DEFAULT_CONFIG_FILE
        self._config: Optional[AppConfig] = None

    def _ensure_config_dir(self) -> None:
        """Ensure the config directory exists."""
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def load(self) -> AppConfig:
        """Load configuration from file.

        Returns:
            AppConfig instance (creates default if file doesn't exist)
        """
        if self._config is not None:
            return self._config

        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    self._config = AppConfig(**data)
                    logger.info(f"Loaded config from {self.config_file}")
            else:
                logger.info("Config file not found, using defaults")
                self._config = AppConfig()
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse config file: {e}")
            self._config = AppConfig()
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            self._config = AppConfig()

        return self._config

    def save(self, config: Optional[AppConfig] = None) -> bool:
        """Save configuration to file.

        Args:
            config: Config to save (uses cached config if not provided)

        Returns:
            True if save was successful
        """
        if config is not None:
            self._config = config

        if self._config is None:
            logger.warning("No config to save")
            return False

        try:
            self._ensure_config_dir()
            with open(self.config_file, 'w') as f:
                json.dump(self._config.model_dump(), f, indent=2)
            logger.info(f"Saved config to {self.config_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
            return False

    def get_config(self) -> AppConfig:
        """Get the current configuration (loads if not cached).

        Returns:
            Current AppConfig instance
        """
        if self._config is None:
            return self.load()
        return self._config

    def update_llm_config(self, **kwargs) -> AppConfig:
        """Update LLM configuration.

        Args:
            **kwargs: LLM config fields to update

        Returns:
            Updated AppConfig
        """
        config = self.get_config()
        for key, value in kwargs.items():
            if hasattr(config.llm, key):
                setattr(config.llm, key, value)
        self.save(config)
        return config

    def update_chesscom_username(self, username: str) -> AppConfig:
        """Update Chess.com username.

        Args:
            username: New Chess.com username

        Returns:
            Updated AppConfig
        """
        config = self.get_config()
        config.chesscom_username = username
        self.save(config)
        return config

    def update_account_user_id(self, user_id: int) -> AppConfig:
        """Update the linked account user ID.

        Args:
            user_id: User ID from the API

        Returns:
            Updated AppConfig
        """
        config = self.get_config()
        config.account_user_id = user_id
        self.save(config)
        return config

    def get_active_api_key(self) -> Optional[str]:
        """Get the API key for the currently selected LLM provider.

        Returns:
            API key string or None if not configured
        """
        config = self.get_config()
        provider = config.llm.provider

        if provider == "anthropic":
            return config.llm.anthropic_api_key or None
        elif provider == "openai":
            return config.llm.openai_api_key or None
        elif provider == "gemini":
            return config.llm.gemini_api_key or None
        elif provider == "local":
            return config.llm.local_endpoint or None

        return None

    def is_llm_configured(self) -> bool:
        """Check if the LLM provider is properly configured.

        Returns:
            True if the selected provider has valid configuration
        """
        config = self.get_config()
        provider = config.llm.provider

        if provider == "anthropic":
            return bool(config.llm.anthropic_api_key)
        elif provider == "openai":
            return bool(config.llm.openai_api_key)
        elif provider == "gemini":
            return bool(config.llm.gemini_api_key)
        elif provider == "local":
            return bool(config.llm.local_endpoint)

        return False
