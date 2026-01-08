"""Game viewer widget for viewing and navigating through a game."""

import logging
from typing import Optional

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QListWidget, QListWidgetItem, QFrame
)
from PyQt6.QtCore import Qt, QRect, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QPen, QFont

from shared.chess_service import ChessGameService, PGNService

logger = logging.getLogger(__name__)


class MiniChessBoard(QWidget):
    """Compact chess board for game viewing."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.game_service = ChessGameService()
        self.square_size = 45
        self.light_color = QColor('#E8D0AA')
        self.dark_color = QColor('#B58863')

        board_size = self.square_size * 8
        self.setFixedSize(board_size, board_size)

    def paintEvent(self, event):
        """Paint the board."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw squares
        for rank in range(8):
            for file in range(8):
                color = self.light_color if (rank + file) % 2 == 0 else self.dark_color
                rect = QRect(
                    file * self.square_size,
                    (7 - rank) * self.square_size,
                    self.square_size,
                    self.square_size
                )
                painter.fillRect(rect, color)

        # Draw pieces
        font = QFont()
        font.setPointSize(int(self.square_size * 0.55))
        painter.setFont(font)

        for rank in range(8):
            for file in range(8):
                square_name = chr(97 + file) + str(rank + 1)
                piece_info = self.game_service.get_piece_at_square(square_name)

                if piece_info:
                    symbol = piece_info['unicode_symbol']
                    is_white = piece_info['color'] == 'white'

                    rect = QRect(
                        file * self.square_size,
                        (7 - rank) * self.square_size,
                        self.square_size,
                        self.square_size
                    )

                    # Shadow
                    painter.setPen(QPen(QColor(0, 0, 0, 60)))
                    shadow_rect = rect.translated(1, 1)
                    painter.drawText(shadow_rect, Qt.AlignmentFlag.AlignCenter, symbol)

                    # Piece
                    color = QColor('#FFFFFF') if is_white else QColor('#000000')
                    painter.setPen(QPen(color))
                    painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, symbol)

    def load_pgn(self, pgn_data: str) -> bool:
        """Load a game from PGN."""
        try:
            loaded = PGNService.import_game_from_pgn(pgn_data)
            if loaded:
                self.game_service = loaded
                self.update()
                return True
        except Exception as e:
            logger.error(f"Failed to load PGN: {e}")
        return False

    def goto_move(self, index: int):
        """Go to a specific move."""
        self.game_service.goto_move(index)
        self.update()

    def reset(self):
        """Reset to starting position."""
        self.game_service.reset_game()
        self.update()


class GameViewerWidget(QWidget):
    """Widget for viewing and navigating through a chess game."""

    move_selected = pyqtSignal(int)  # move_index

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_move_index = -1
        self._setup_ui()

    def _setup_ui(self):
        """Set up the viewer UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header
        header = QFrame()
        header.setStyleSheet("background-color: #1a1a2e;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(15, 12, 15, 12)

        title = QLabel("Game Viewer")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #ffffff;")
        header_layout.addWidget(title)

        header_layout.addStretch()

        self._move_label = QLabel("Move: -")
        self._move_label.setStyleSheet("color: #888888;")
        header_layout.addWidget(self._move_label)

        layout.addWidget(header)

        # Board and moves container
        content = QFrame()
        content.setStyleSheet("background-color: #16213e;")
        content_layout = QHBoxLayout(content)
        content_layout.setContentsMargins(15, 15, 15, 15)
        content_layout.setSpacing(15)

        # Board
        board_container = QWidget()
        board_layout = QVBoxLayout(board_container)
        board_layout.setContentsMargins(0, 0, 0, 0)
        board_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._board = MiniChessBoard()
        board_layout.addWidget(self._board)

        content_layout.addWidget(board_container)

        # Move list
        moves_container = QWidget()
        moves_layout = QVBoxLayout(moves_container)
        moves_layout.setContentsMargins(0, 0, 0, 0)
        moves_layout.setSpacing(8)

        moves_label = QLabel("Moves")
        moves_label.setStyleSheet("color: #ffffff; font-weight: bold;")
        moves_layout.addWidget(moves_label)

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
        """)
        self._move_list.setMinimumWidth(150)
        self._move_list.itemClicked.connect(self._on_move_clicked)
        moves_layout.addWidget(self._move_list, stretch=1)

        content_layout.addWidget(moves_container)

        layout.addWidget(content, stretch=1)

        # Navigation controls
        nav_frame = QFrame()
        nav_frame.setStyleSheet("background-color: #1a1a2e;")
        nav_layout = QHBoxLayout(nav_frame)
        nav_layout.setContentsMargins(15, 10, 15, 10)
        nav_layout.setSpacing(8)

        self._first_btn = self._create_nav_btn("⏮", "First move")
        self._first_btn.clicked.connect(self._goto_first)
        nav_layout.addWidget(self._first_btn)

        self._prev_btn = self._create_nav_btn("◀", "Previous move")
        self._prev_btn.clicked.connect(self._goto_prev)
        nav_layout.addWidget(self._prev_btn)

        self._next_btn = self._create_nav_btn("▶", "Next move")
        self._next_btn.clicked.connect(self._goto_next)
        nav_layout.addWidget(self._next_btn)

        self._last_btn = self._create_nav_btn("⏭", "Last move")
        self._last_btn.clicked.connect(self._goto_last)
        nav_layout.addWidget(self._last_btn)

        nav_layout.addStretch()

        layout.addWidget(nav_frame)

    def _create_nav_btn(self, text: str, tooltip: str) -> QPushButton:
        """Create a navigation button."""
        btn = QPushButton(text)
        btn.setToolTip(tooltip)
        btn.setStyleSheet("""
            QPushButton {
                background-color: #253156;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #3a4a6a;
            }
            QPushButton:pressed {
                background-color: #4a9eff;
            }
        """)
        return btn

    def load_game(self, pgn_data: str):
        """Load a game to view."""
        if self._board.load_pgn(pgn_data):
            self._populate_move_list()
            self._current_move_index = len(self._board.game_service.get_move_history_san()) - 1
            self._update_display()

    def _populate_move_list(self):
        """Populate the move list."""
        self._move_list.clear()
        moves = self._board.game_service.get_move_history_san()

        for i in range(0, len(moves), 2):
            move_num = i // 2 + 1
            white_move = moves[i]
            black_move = moves[i + 1] if i + 1 < len(moves) else ""

            if black_move:
                text = f"{move_num}. {white_move} {black_move}"
            else:
                text = f"{move_num}. {white_move}"

            item = QListWidgetItem(text)
            item.setData(Qt.ItemDataRole.UserRole, i)
            self._move_list.addItem(item)

    def _update_display(self):
        """Update the display after navigation."""
        self._board.goto_move(self._current_move_index)

        total_moves = len(self._board.game_service.get_move_history_san())
        if self._current_move_index < 0:
            self._move_label.setText("Starting position")
        else:
            self._move_label.setText(f"Move: {self._current_move_index + 1}/{total_moves}")

        # Highlight current move in list
        list_index = self._current_move_index // 2 if self._current_move_index >= 0 else -1
        if 0 <= list_index < self._move_list.count():
            self._move_list.setCurrentRow(list_index)

    def _on_move_clicked(self, item: QListWidgetItem):
        """Handle move list click."""
        move_index = item.data(Qt.ItemDataRole.UserRole)
        if move_index is not None:
            self._current_move_index = move_index
            self._update_display()
            self.move_selected.emit(move_index)

    def _goto_first(self):
        """Go to the first move."""
        self._current_move_index = -1
        self._update_display()

    def _goto_prev(self):
        """Go to the previous move."""
        if self._current_move_index > -1:
            self._current_move_index -= 1
            self._update_display()

    def _goto_next(self):
        """Go to the next move."""
        total = len(self._board.game_service.get_move_history_san())
        if self._current_move_index < total - 1:
            self._current_move_index += 1
            self._update_display()

    def _goto_last(self):
        """Go to the last move."""
        total = len(self._board.game_service.get_move_history_san())
        self._current_move_index = total - 1
        self._update_display()

    def get_current_position(self) -> dict:
        """Get current position info."""
        return {
            "fen": self._board.game_service.get_fen(),
            "move_index": self._current_move_index
        }

    def clear(self):
        """Clear the viewer."""
        self._board.reset()
        self._move_list.clear()
        self._current_move_index = -1
        self._move_label.setText("Move: -")
