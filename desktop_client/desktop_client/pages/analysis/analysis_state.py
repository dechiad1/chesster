"""Analysis page state management."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class AnalysisState:
    """State container for analysis page."""
    selected_game_id: Optional[int] = None
    analysis_in_progress: bool = False
