"""Settings page state management."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class SettingsState:
    """State container for settings page."""
    has_unsaved_changes: bool = False
    current_user_id: Optional[int] = None
