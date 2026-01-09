"""Chess board widget for game play."""

import logging
from typing import Optional

import chess
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QRect, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QPen, QFont

from shared.chess_service import ChessGameService

logger = logging.getLogger(__name__)


class ChessBoardWidget(QWidget):
    """Chess board widget with click-to-move functionality."""

    move_made = pyqtSignal(str)  # Emits the move in UCI format
    position_changed = pyqtSignal()  # Emits when position changes (including goto)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.game_service = ChessGameService()

        # Visual settings
        self.selected_square: Optional[int] = None
        self.square_size = 60
        self.light_square_color = QColor('#E8D0AA')
        self.dark_square_color = QColor('#B58863')
        self.selected_square_color = QColor(255, 255, 0, 100)
        self.last_move_color = QColor(155, 199, 0, 100)
        self.legal_move_color = QColor(0, 0, 0, 40)

        # Track last move for highlighting
        self._last_move_from: Optional[int] = None
        self._last_move_to: Optional[int] = None

        # Set minimum size
        board_size = self.square_size * 8
        self.setMinimumSize(board_size, board_size)
        self.setMaximumSize(board_size + 40, board_size + 40)

    def paintEvent(self, event):
        """Paint the chess board."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Calculate board offset for centering
        offset_x = (self.width() - self.square_size * 8) // 2
        offset_y = (self.height() - self.square_size * 8) // 2

        # Draw squares
        for rank in range(8):
            for file in range(8):
                color = self.light_square_color if (rank + file) % 2 == 0 else self.dark_square_color
                square = QRect(
                    offset_x + file * self.square_size,
                    offset_y + (7 - rank) * self.square_size,
                    self.square_size,
                    self.square_size
                )
                painter.fillRect(square, color)

                # Highlight last move
                square_index = rank * 8 + file
                if square_index == self._last_move_from or square_index == self._last_move_to:
                    painter.fillRect(square, self.last_move_color)

                # Highlight selected square
                if self.selected_square is not None:
                    selected_file = self.selected_square % 8
                    selected_rank = self.selected_square // 8
                    if file == selected_file and rank == selected_rank:
                        painter.fillRect(square, self.selected_square_color)

        # Draw legal move indicators when a piece is selected
        if self.selected_square is not None:
            from_square = chr(97 + (self.selected_square % 8)) + str((self.selected_square // 8) + 1)
            legal_moves = self.game_service.get_legal_moves()

            for move in legal_moves:
                move_uci = move.uci()
                if move_uci.startswith(from_square):
                    to_square = move_uci[2:4]
                    to_file = ord(to_square[0]) - 97
                    to_rank = int(to_square[1]) - 1

                    center_x = offset_x + to_file * self.square_size + self.square_size // 2
                    center_y = offset_y + (7 - to_rank) * self.square_size + self.square_size // 2
                    radius = self.square_size // 6

                    painter.setBrush(self.legal_move_color)
                    painter.setPen(Qt.PenStyle.NoPen)
                    painter.drawEllipse(center_x - radius, center_y - radius, radius * 2, radius * 2)

        # Draw pieces
        font = QFont()
        font.setPointSize(int(self.square_size * 0.6))
        painter.setFont(font)

        for rank in range(8):
            for file in range(8):
                square_name = chr(97 + file) + str(rank + 1)
                piece_info = self.game_service.get_piece_at_square(square_name)

                if piece_info:
                    symbol = piece_info['unicode_symbol']
                    is_white = piece_info['color'] == 'white'

                    # Draw piece with shadow effect
                    rect = QRect(
                        offset_x + file * self.square_size,
                        offset_y + (7 - rank) * self.square_size,
                        self.square_size,
                        self.square_size
                    )

                    # Shadow
                    painter.setPen(QPen(QColor(0, 0, 0, 80)))
                    shadow_rect = rect.translated(2, 2)
                    painter.drawText(shadow_rect, Qt.AlignmentFlag.AlignCenter, symbol)

                    # Piece
                    color = QColor('#FFFFFF') if is_white else QColor('#000000')
                    painter.setPen(QPen(color))
                    painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, symbol)

        # Draw coordinates
        coord_font = QFont()
        coord_font.setPointSize(9)
        painter.setFont(coord_font)
        painter.setPen(QPen(QColor('#666666')))

        for i in range(8):
            # Rank numbers (1-8)
            rank_rect = QRect(offset_x - 20, offset_y + (7 - i) * self.square_size, 15, self.square_size)
            painter.drawText(rank_rect, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight, str(i + 1))

            # File letters (a-h)
            file_rect = QRect(offset_x + i * self.square_size, offset_y + 8 * self.square_size, self.square_size, 20)
            painter.drawText(file_rect, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop, chr(97 + i))

    def mousePressEvent(self, event):
        """Handle mouse clicks on the board."""
        # Calculate board offset
        offset_x = (self.width() - self.square_size * 8) // 2
        offset_y = (self.height() - self.square_size * 8) // 2

        # Calculate clicked square
        file = int((event.position().x() - offset_x) // self.square_size)
        rank = int((event.position().y() - offset_y) // self.square_size)
        rank = 7 - rank  # Flip rank for proper coordinates

        if not (0 <= file < 8 and 0 <= rank < 8):
            return

        square = rank * 8 + file
        square_name = chr(97 + file) + str(rank + 1)

        if self.selected_square is None:
            # Select a square if it has a piece of the current turn's color
            piece_info = self.game_service.get_piece_at_square(square_name)
            if piece_info and piece_info['color'] == self.game_service.get_current_turn():
                self.selected_square = square
                self.update()
        else:
            # Try to make a move
            from_file = self.selected_square % 8
            from_rank = self.selected_square // 8
            from_square = chr(97 + from_file) + str(from_rank + 1)
            move_uci = from_square + square_name

            # Check for pawn promotion
            piece_info = self.game_service.get_piece_at_square(from_square)
            if piece_info and piece_info['type'] == chess.PAWN:
                if (piece_info['color'] == 'white' and rank == 7) or \
                   (piece_info['color'] == 'black' and rank == 0):
                    move_uci += 'q'  # Auto-promote to queen

            if self._try_make_move(move_uci):
                self._last_move_from = self.selected_square
                self._last_move_to = square

            self.selected_square = None
            self.update()

    def _try_make_move(self, move: str) -> bool:
        """Try to make a move.

        Args:
            move: Move in UCI format

        Returns:
            True if move was successful
        """
        try:
            success = self.game_service.make_move_from_uci(move)
            if success:
                self.move_made.emit(move)
                self.position_changed.emit()
                return True
            return False
        except Exception as e:
            logger.error(f"Error making move: {e}")
            return False

    def new_game(self):
        """Start a new game."""
        self.game_service.reset_game()
        self.selected_square = None
        self._last_move_from = None
        self._last_move_to = None
        self.position_changed.emit()
        self.update()

    def load_pgn(self, pgn_data: str) -> bool:
        """Load a game from PGN data.

        Args:
            pgn_data: PGN string

        Returns:
            True if successful
        """
        from shared.chess_service import PGNService
        try:
            loaded_service = PGNService.import_game_from_pgn(pgn_data)
            if loaded_service:
                self.game_service = loaded_service
                self.selected_square = None
                self._last_move_from = None
                self._last_move_to = None
                self.position_changed.emit()
                self.update()
                return True
        except Exception as e:
            logger.error(f"Failed to load PGN: {e}")
        return False

    def goto_move(self, index: int):
        """Go to a specific move in the game.

        Args:
            index: Move index (0-based)
        """
        self.game_service.goto_move(index)
        self.selected_square = None
        self.position_changed.emit()
        self.update()

    def undo_move(self) -> bool:
        """Undo the last move.

        Returns:
            True if successful
        """
        if self.game_service.undo_move():
            self.selected_square = None
            self._last_move_from = None
            self._last_move_to = None
            self.position_changed.emit()
            self.update()
            return True
        return False

    def get_fen(self) -> str:
        """Get the current FEN position."""
        return self.game_service.get_board_fen()

    def get_pgn(self) -> str:
        """Get the current game as PGN."""
        from shared.chess_service import PGNService
        return PGNService.export_game_to_pgn(
            self.game_service,
            event="Desktop Game",
            site="Chesster",
            white="Player",
            black="Opponent"
        )

    def get_move_history_san(self) -> list[str]:
        """Get the move history in SAN notation."""
        return self.game_service.get_move_history_san()

    def get_current_turn(self) -> str:
        """Get whose turn it is."""
        return self.game_service.get_current_turn()

    def is_game_over(self) -> bool:
        """Check if the game is over."""
        return self.game_service.is_game_over()

    def get_game_result(self) -> str:
        """Get the game result."""
        return self.game_service.get_game_result()

    def is_in_check(self) -> bool:
        """Check if the current player is in check."""
        return self.game_service.is_check()
