"""Game page state management."""

import logging
from typing import Optional
from dataclasses import dataclass, field

from shared.chess_service import ChessGameService, PGNService, OpeningBook

logger = logging.getLogger(__name__)


@dataclass
class GameState:
    """State container for the game page."""
    current_game_id: Optional[int] = None
    is_modified: bool = False
    auto_save_enabled: bool = True


class GameStateManager:
    """Manages game state and coordinates between components."""

    def __init__(self):
        self._state = GameState()
        self._opening_book = OpeningBook()

    @property
    def state(self) -> GameState:
        """Get the current state."""
        return self._state

    @property
    def current_game_id(self) -> Optional[int]:
        """Get the current game ID."""
        return self._state.current_game_id

    @current_game_id.setter
    def current_game_id(self, value: Optional[int]):
        """Set the current game ID."""
        self._state.current_game_id = value

    @property
    def is_modified(self) -> bool:
        """Check if the current game has unsaved changes."""
        return self._state.is_modified

    def mark_modified(self):
        """Mark the current game as modified."""
        self._state.is_modified = True

    def mark_saved(self):
        """Mark the current game as saved."""
        self._state.is_modified = False

    def reset(self):
        """Reset the state for a new game."""
        self._state = GameState()

    def load_opening(self, name: str, game_service: ChessGameService) -> bool:
        """Load an opening into the game service.

        Args:
            name: Opening name
            game_service: Game service to load into

        Returns:
            True if successful
        """
        try:
            success = self._opening_book.load_opening_to_service(name, game_service)
            if success:
                self._state.current_game_id = None
                self._state.is_modified = True
            return success
        except Exception as e:
            logger.error(f"Failed to load opening: {e}")
            return False
