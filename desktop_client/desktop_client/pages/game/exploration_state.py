"""State management for chess line exploration mode."""

from dataclasses import dataclass, field
from typing import Optional, List, Tuple

import chess

from desktop_client.pages.game.models import ChessLine


@dataclass
class ExplorationState:
    """State for line exploration mode."""
    is_active: bool = False
    current_line: Optional[ChessLine] = None
    current_position: int = 0  # Which move in the line we're viewing

    # Saved game state
    saved_fen: Optional[str] = None
    saved_move_index: int = -1
    saved_move_history: List[Tuple[chess.Move, str]] = field(default_factory=list)


class ExplorationStateManager:
    """Manages exploration mode and state transitions."""

    def __init__(self):
        self.state = ExplorationState()

    def enter_exploration(
        self,
        line: ChessLine,
        current_fen: str,
        current_move_index: int,
        move_history: List[Tuple[chess.Move, str]]
    ):
        """Enter exploration mode, saving current game state.

        Args:
            line: The chess line to explore
            current_fen: Current board position FEN
            current_move_index: Current move index in game history
            move_history: Full move history of the current game
        """
        self.state = ExplorationState(
            is_active=True,
            current_line=line,
            current_position=0,
            saved_fen=current_fen,
            saved_move_index=current_move_index,
            saved_move_history=move_history.copy() if move_history else []
        )

    def exit_exploration(self) -> tuple[str, int]:
        """Exit exploration mode, returning saved state.

        Returns:
            Tuple of (saved_fen, saved_move_index)
        """
        saved_fen = self.state.saved_fen
        saved_index = self.state.saved_move_index

        self.state = ExplorationState()

        return saved_fen, saved_index

    def next_position(self) -> int:
        """Move to next position in line.

        Returns:
            Updated position index
        """
        if self.state.current_line and self.state.current_position < len(self.state.current_line.moves):
            self.state.current_position += 1
        return self.state.current_position

    def previous_position(self) -> int:
        """Move to previous position in line.

        Returns:
            Updated position index
        """
        if self.state.current_position > 0:
            self.state.current_position -= 1
        return self.state.current_position

    def get_current_move_uci(self) -> Optional[str]:
        """Get the UCI move at the current position.

        Returns:
            UCI move string or None
        """
        if not self.state.current_line or self.state.current_position == 0:
            return None

        move_index = self.state.current_position - 1
        if 0 <= move_index < len(self.state.current_line.moves):
            return self.state.current_line.moves[move_index]

        return None
