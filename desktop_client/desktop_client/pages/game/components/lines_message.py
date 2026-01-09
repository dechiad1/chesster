"""Lines suggestion message widget for coach chat."""

from typing import List

from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QFont

from desktop_client.pages.game.models import ChessLine
from desktop_client.pages.game.components.line_card import LineCardWidget


class LinesSuggestionMessage(QFrame):
    """Chat message widget displaying suggested chess lines."""

    line_selected = pyqtSignal(object)  # Emits ChessLine when user clicks a card

    def __init__(self, lines: List[ChessLine], intro_text: str = None, parent=None):
        super().__init__(parent)
        self._lines = lines
        self._intro_text = intro_text or "Here are some typical continuations. Click one to explore:"
        self._setup_ui()

    def _setup_ui(self):
        """Set up the message UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(8)

        # Sender label
        sender_label = QLabel("Coach")
        sender_font = QFont()
        sender_font.setBold(True)
        sender_font.setPointSize(10)
        sender_label.setFont(sender_font)
        sender_label.setStyleSheet("color: #5cb85c;")
        layout.addWidget(sender_label)

        # Intro text
        intro = QLabel(self._intro_text)
        intro.setStyleSheet("color: #d0d0d0; margin-bottom: 4px;")
        intro.setWordWrap(True)
        layout.addWidget(intro)

        # Line cards
        for line in self._lines:
            card = LineCardWidget(line)
            card.line_clicked.connect(self.line_selected.emit)
            layout.addWidget(card)

        # Styling
        self.setStyleSheet("""
            LinesSuggestionMessage {
                background-color: #1e2746;
                border-radius: 8px;
                margin-right: 40px;
            }
        """)
