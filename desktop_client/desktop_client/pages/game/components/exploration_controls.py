"""Exploration controls widget for navigating chess line variations."""

from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QFont


class ExplorationControlsWidget(QFrame):
    """Controls for navigating through a chess line exploration."""

    previous_move = pyqtSignal()
    next_move = pyqtSignal()
    exit_exploration = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_position = 0
        self._total_positions = 0
        self._setup_ui()

    def _setup_ui(self):
        """Set up controls UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(10)

        # Title
        title = QLabel("Exploring Line")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(12)
        title.setFont(title_font)
        title.setStyleSheet("color: #ffc107;")
        layout.addWidget(title)

        # Position indicator
        self._position_label = QLabel("Position 0 / 0")
        self._position_label.setStyleSheet("color: #c0c0c0; font-size: 11px;")
        layout.addWidget(self._position_label)

        # Navigation buttons
        nav_layout = QHBoxLayout()
        nav_layout.setSpacing(8)

        self._prev_btn = QPushButton("← Previous")
        self._prev_btn.clicked.connect(self.previous_move.emit)
        self._prev_btn.setStyleSheet(self._button_style("#6c757d"))
        nav_layout.addWidget(self._prev_btn)

        self._next_btn = QPushButton("Next →")
        self._next_btn.clicked.connect(self.next_move.emit)
        self._next_btn.setStyleSheet(self._button_style("#6c757d"))
        nav_layout.addWidget(self._next_btn)

        layout.addLayout(nav_layout)

        # Exit button (prominent)
        self._exit_btn = QPushButton("← Back to Game")
        self._exit_btn.clicked.connect(self.exit_exploration.emit)
        self._exit_btn.setStyleSheet(self._button_style("#dc3545"))
        layout.addWidget(self._exit_btn)

        # Frame styling
        self.setStyleSheet("""
            ExplorationControlsWidget {
                background-color: #2a3a1e;
                border: 2px solid #ffc107;
                border-radius: 8px;
            }
        """)

    def update_position(self, current: int, total: int):
        """Update position display and button states.

        Args:
            current: Current position index (0-based)
            total: Total number of positions
        """
        self._current_position = current
        self._total_positions = total
        self._position_label.setText(f"Position {current} / {total}")

        # Enable/disable buttons
        self._prev_btn.setEnabled(current > 0)
        self._next_btn.setEnabled(current < total)

    def _button_style(self, color: str) -> str:
        """Get button stylesheet with the specified color.

        Args:
            color: Background color for the button

        Returns:
            CSS stylesheet string
        """
        return f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                opacity: 0.9;
            }}
            QPushButton:disabled {{
                background-color: #3a4a5a;
                color: #888888;
            }}
        """
