"""Game controls widget for game management."""

import logging
from typing import Optional

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QListWidget, QListWidgetItem, QFrame, QMessageBox, QFileDialog,
    QComboBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from shared.chess_service import OpeningBook

logger = logging.getLogger(__name__)


class GameControlsWidget(QWidget):
    """Widget for game controls and move history."""

    new_game_requested = pyqtSignal()
    save_game_requested = pyqtSignal()
    load_game_requested = pyqtSignal(int)  # game_id
    load_pgn_requested = pyqtSignal(str)  # pgn_data
    export_pgn_requested = pyqtSignal()
    undo_requested = pyqtSignal()
    goto_move_requested = pyqtSignal(int)  # move_index
    opening_selected = pyqtSignal(str)  # opening_name

    def __init__(self, parent=None):
        super().__init__(parent)
        self._opening_book = OpeningBook()
        self._setup_ui()

    def _setup_ui(self):
        """Set up the controls UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Game info header
        header = QFrame()
        header.setStyleSheet("background-color: #1a1a2e; padding: 10px;")
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(15, 10, 15, 10)
        header_layout.setSpacing(5)

        title_label = QLabel("Game Controls")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #ffffff;")
        header_layout.addWidget(title_label)

        self._status_label = QLabel("White to move")
        self._status_label.setStyleSheet("color: #888888; font-size: 12px;")
        header_layout.addWidget(self._status_label)

        layout.addWidget(header)

        # Control buttons
        buttons_frame = QFrame()
        buttons_frame.setStyleSheet("background-color: #16213e;")
        buttons_layout = QVBoxLayout(buttons_frame)
        buttons_layout.setContentsMargins(10, 10, 10, 10)
        buttons_layout.setSpacing(8)

        # Row 1: New Game, Undo
        row1 = QHBoxLayout()
        row1.setSpacing(8)

        self._new_game_btn = self._create_button("New Game", "#4a9eff")
        self._new_game_btn.clicked.connect(self._on_new_game)
        row1.addWidget(self._new_game_btn)

        self._undo_btn = self._create_button("Undo", "#6c757d")
        self._undo_btn.clicked.connect(self.undo_requested.emit)
        row1.addWidget(self._undo_btn)

        buttons_layout.addLayout(row1)

        # Row 2: Save, Load
        row2 = QHBoxLayout()
        row2.setSpacing(8)

        self._save_btn = self._create_button("Save", "#28a745")
        self._save_btn.clicked.connect(self.save_game_requested.emit)
        row2.addWidget(self._save_btn)

        self._load_btn = self._create_button("Load PGN", "#6c757d")
        self._load_btn.clicked.connect(self._on_load_pgn)
        row2.addWidget(self._load_btn)

        buttons_layout.addLayout(row2)

        # Export button
        self._export_btn = self._create_button("Export PGN", "#17a2b8")
        self._export_btn.clicked.connect(self.export_pgn_requested.emit)
        buttons_layout.addWidget(self._export_btn)

        layout.addWidget(buttons_frame)

        # Opening book section
        openings_frame = QFrame()
        openings_frame.setStyleSheet("background-color: #16213e;")
        openings_layout = QVBoxLayout(openings_frame)
        openings_layout.setContentsMargins(10, 10, 10, 10)
        openings_layout.setSpacing(8)

        openings_label = QLabel("Opening Book")
        openings_label.setStyleSheet("color: #ffffff; font-weight: bold;")
        openings_layout.addWidget(openings_label)

        self._openings_combo = QComboBox()
        self._openings_combo.setStyleSheet("""
            QComboBox {
                background-color: #253156;
                color: #ffffff;
                border: 1px solid #3a4a6a;
                border-radius: 4px;
                padding: 6px;
            }
            QComboBox:hover {
                border-color: #4a9eff;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #253156;
                color: #ffffff;
                selection-background-color: #4a9eff;
            }
        """)
        self._openings_combo.addItem("Select an opening...")
        for name in self._opening_book.get_all_openings().keys():
            self._openings_combo.addItem(name)
        self._openings_combo.currentTextChanged.connect(self._on_opening_selected)
        openings_layout.addWidget(self._openings_combo)

        layout.addWidget(openings_frame)

        # Move history
        history_frame = QFrame()
        history_frame.setStyleSheet("background-color: #16213e;")
        history_layout = QVBoxLayout(history_frame)
        history_layout.setContentsMargins(10, 10, 10, 10)
        history_layout.setSpacing(8)

        history_label = QLabel("Move History")
        history_label.setStyleSheet("color: #ffffff; font-weight: bold;")
        history_layout.addWidget(history_label)

        self._move_list = QListWidget()
        self._move_list.setStyleSheet("""
            QListWidget {
                background-color: #253156;
                color: #e0e0e0;
                border: 1px solid #3a4a6a;
                border-radius: 4px;
            }
            QListWidget::item {
                padding: 4px 8px;
            }
            QListWidget::item:selected {
                background-color: #4a9eff;
            }
            QListWidget::item:hover {
                background-color: #2a4570;
            }
        """)
        self._move_list.itemClicked.connect(self._on_move_clicked)
        history_layout.addWidget(self._move_list, stretch=1)

        layout.addWidget(history_frame, stretch=1)

    def _create_button(self, text: str, color: str) -> QPushButton:
        """Create a styled button."""
        btn = QPushButton(text)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self._lighten_color(color)};
            }}
            QPushButton:pressed {{
                background-color: {self._darken_color(color)};
            }}
            QPushButton:disabled {{
                background-color: #3a4a5a;
                color: #888888;
            }}
        """)
        return btn

    def _lighten_color(self, hex_color: str) -> str:
        """Lighten a hex color."""
        # Simple approximation
        return hex_color.replace('#', '#')  # Would need proper implementation

    def _darken_color(self, hex_color: str) -> str:
        """Darken a hex color."""
        return hex_color.replace('#', '#')  # Would need proper implementation

    def _on_new_game(self):
        """Handle new game button click."""
        reply = QMessageBox.question(
            self,
            "New Game",
            "Start a new game? Current game will be saved automatically.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.new_game_requested.emit()

    def _on_load_pgn(self):
        """Handle load PGN button click."""
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Open PGN File",
            "",
            "PGN files (*.pgn);;All files (*)"
        )
        if file_name:
            try:
                with open(file_name, 'r') as f:
                    pgn_data = f.read()
                self.load_pgn_requested.emit(pgn_data)
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Load Error",
                    f"Failed to load PGN file: {e}"
                )

    def _on_opening_selected(self, name: str):
        """Handle opening selection."""
        if name and name != "Select an opening...":
            self.opening_selected.emit(name)
            # Reset combo to placeholder
            self._openings_combo.setCurrentIndex(0)

    def _on_move_clicked(self, item: QListWidgetItem):
        """Handle move list item click."""
        row = self._move_list.row(item)
        # Each row contains a move pair, so calculate the actual move index
        move_index = row * 2
        # If the item text contains a second move, clicking should go to that move
        text = item.text()
        if '...' in text or len(text.split()) > 2:
            # Could implement more precise click detection here
            pass
        self.goto_move_requested.emit(move_index)

    def update_status(self, turn: str, is_check: bool, is_game_over: bool, result: str):
        """Update the game status display.

        Args:
            turn: Current player's turn ('white' or 'black')
            is_check: Whether the current player is in check
            is_game_over: Whether the game is over
            result: Game result if over
        """
        if is_game_over:
            self._status_label.setText(f"Game Over: {result}")
            self._status_label.setStyleSheet("color: #ffc107; font-size: 12px;")
        elif is_check:
            self._status_label.setText(f"{turn.title()} to move (Check!)")
            self._status_label.setStyleSheet("color: #dc3545; font-size: 12px;")
        else:
            self._status_label.setText(f"{turn.title()} to move")
            self._status_label.setStyleSheet("color: #888888; font-size: 12px;")

    def update_move_list(self, moves: list[str]):
        """Update the move history list.

        Args:
            moves: List of moves in SAN notation
        """
        self._move_list.clear()
        for i in range(0, len(moves), 2):
            move_num = i // 2 + 1
            white_move = moves[i]
            black_move = moves[i + 1] if i + 1 < len(moves) else ""

            if black_move:
                text = f"{move_num}. {white_move}  {black_move}"
            else:
                text = f"{move_num}. {white_move}"

            self._move_list.addItem(text)

        # Scroll to bottom
        if self._move_list.count() > 0:
            self._move_list.scrollToBottom()

    def clear(self):
        """Clear the controls state."""
        self._move_list.clear()
        self._status_label.setText("White to move")
        self._status_label.setStyleSheet("color: #888888; font-size: 12px;")
        self._openings_combo.setCurrentIndex(0)
