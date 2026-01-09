"""Line card widget for displaying suggested chess variations."""

from typing import List

from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont, QCursor

from desktop_client.pages.game.models import ChessLine


class LineCardWidget(QFrame):
    """Widget displaying a single chess line/variation as a clickable card."""

    line_clicked = pyqtSignal(object)  # Emits ChessLine when clicked

    def __init__(self, line: ChessLine, parent=None):
        super().__init__(parent)
        self._line = line
        self._setup_ui()

    def _setup_ui(self):
        """Set up the card UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(6)

        # Description
        desc_label = QLabel(self._line.description)
        desc_label.setStyleSheet("color: #ffffff; font-weight: bold; font-size: 13px;")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)

        # Moves display (formatted as "1. e4 e5 2. Nf3 Nc6...")
        moves_text = self._format_moves(self._line.moves_san)
        moves_label = QLabel(moves_text)
        moves_label.setWordWrap(True)
        moves_label.setStyleSheet(
            "color: #c0c0c0; font-size: 12px; font-family: 'Courier New', monospace;"
        )
        layout.addWidget(moves_label)

        # Evaluation if available
        if self._line.evaluation is not None:
            eval_text = f"Evaluation: {self._line.evaluation / 100:.2f}"
            eval_label = QLabel(eval_text)
            eval_label.setStyleSheet("color: #888888; font-size: 11px;")
            layout.addWidget(eval_label)

        # Styling for card
        self.setStyleSheet("""
            LineCardWidget {
                background-color: #253156;
                border: 2px solid #3a4a6a;
                border-radius: 8px;
            }
            LineCardWidget:hover {
                border-color: #4a9eff;
                background-color: #2a3966;
            }
        """)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

    def mousePressEvent(self, event):
        """Handle click on the card."""
        self.line_clicked.emit(self._line)
        super().mousePressEvent(event)

    def _format_moves(self, moves_san: List[str]) -> str:
        """Format moves as '1. e4 e5 2. Nf3 Nc6'.

        Args:
            moves_san: List of moves in SAN notation

        Returns:
            Formatted move string
        """
        result = []
        for i, move in enumerate(moves_san):
            if i % 2 == 0:
                result.append(f"{i // 2 + 1}. {move}")
            else:
                result[-1] += f" {move}"
        return " ".join(result)
