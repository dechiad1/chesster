"""Chess engine port interface."""

from abc import ABC, abstractmethod
from typing import List, Optional
from pydantic import BaseModel


class PositionAnalysis(BaseModel):
    """Analysis result for a chess position."""
    fen: str
    evaluation: float  # Centipawns from white's perspective
    best_move: str  # UCI format
    depth: int
    pv: List[str]  # Principal variation (best line)
    is_mate: bool = False
    mate_in: Optional[int] = None


class MoveEvaluation(BaseModel):
    """Evaluation of a specific move."""
    move: str  # UCI format
    evaluation_before: float
    evaluation_after: float
    centipawn_loss: float
    is_blunder: bool = False  # > 200 cp loss
    is_mistake: bool = False  # > 100 cp loss
    is_inaccuracy: bool = False  # > 50 cp loss
    best_move: str  # What would have been better
    best_move_eval: float


class ChessEnginePort(ABC):
    """Abstract interface for chess engine analysis.

    Implementations can use Stockfish, LC0, or other engines.
    """

    @abstractmethod
    def analyze_position(self, fen: str, depth: int = 20) -> PositionAnalysis:
        """Analyze a chess position.

        Args:
            fen: Position in FEN notation
            depth: Search depth

        Returns:
            PositionAnalysis with evaluation and best move
        """
        pass

    @abstractmethod
    def evaluate_move(self, fen: str, move: str, depth: int = 20) -> MoveEvaluation:
        """Evaluate a specific move.

        Args:
            fen: Position before the move (FEN)
            move: The move to evaluate (UCI)
            depth: Search depth

        Returns:
            MoveEvaluation with centipawn loss and classification
        """
        pass

    @abstractmethod
    def get_best_move(self, fen: str, depth: int = 20) -> str:
        """Get the best move for a position.

        Args:
            fen: Position in FEN notation
            depth: Search depth

        Returns:
            Best move in UCI format
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the engine is available.

        Returns:
            True if engine is ready to use
        """
        pass
