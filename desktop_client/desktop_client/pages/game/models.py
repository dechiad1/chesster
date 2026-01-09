"""Data models for game page components."""

from dataclasses import dataclass
from typing import List, Optional, Literal


@dataclass
class ChessLine:
    """Represents a chess variation/line."""
    description: str
    moves: List[str]  # UCI format
    moves_san: List[str]  # SAN format for display
    evaluation: Optional[float] = None


@dataclass
class CoachResponse:
    """Structured coach response."""
    response_type: Literal["text", "lines"]
    content: str
    lines: Optional[List[ChessLine]] = None
