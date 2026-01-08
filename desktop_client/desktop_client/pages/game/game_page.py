"""Game page - main chess playing interface."""

import logging
from typing import Optional

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QSplitter, QMessageBox,
    QFileDialog
)
from PyQt6.QtCore import Qt, pyqtSignal

from desktop_client.pages.game.components.chess_board import ChessBoardWidget
from desktop_client.pages.game.components.coach_chat import CoachChatWidget
from desktop_client.pages.game.components.game_controls import GameControlsWidget
from desktop_client.pages.game.game_state import GameStateManager
from desktop_client.services.api_client import ChessAPIClient, APIError
from desktop_client.shared.services.config_service import ConfigService
from shared.chess_service import PGNService

logger = logging.getLogger(__name__)


class GamePage(QWidget):
    """Main game page with chess board, controls, and coach chat."""

    game_saved = pyqtSignal(int)  # Emits game_id when saved

    def __init__(self, parent=None):
        super().__init__(parent)
        self._api_client: Optional[ChessAPIClient] = None
        self._config_service: Optional[ConfigService] = None
        self._state_manager = GameStateManager()

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        """Set up the game page UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Main splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left section: Chess board
        board_container = QWidget()
        board_container.setStyleSheet("background-color: #0d1520;")
        board_layout = QVBoxLayout(board_container)
        board_layout.setContentsMargins(20, 20, 20, 20)
        board_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._chess_board = ChessBoardWidget()
        board_layout.addWidget(self._chess_board, alignment=Qt.AlignmentFlag.AlignCenter)

        splitter.addWidget(board_container)

        # Middle section: Game controls
        self._game_controls = GameControlsWidget()
        self._game_controls.setMinimumWidth(250)
        self._game_controls.setMaximumWidth(300)
        splitter.addWidget(self._game_controls)

        # Right section: Coach chat
        self._coach_chat = CoachChatWidget()
        self._coach_chat.setMinimumWidth(300)
        splitter.addWidget(self._coach_chat)

        # Set splitter sizes
        splitter.setSizes([500, 280, 350])

        layout.addWidget(splitter)

    def _connect_signals(self):
        """Connect component signals."""
        # Chess board signals
        self._chess_board.move_made.connect(self._on_move_made)
        self._chess_board.position_changed.connect(self._update_ui_state)

        # Game controls signals
        self._game_controls.new_game_requested.connect(self._on_new_game)
        self._game_controls.save_game_requested.connect(self._on_save_game)
        self._game_controls.load_pgn_requested.connect(self._on_load_pgn)
        self._game_controls.export_pgn_requested.connect(self._on_export_pgn)
        self._game_controls.undo_requested.connect(self._on_undo)
        self._game_controls.goto_move_requested.connect(self._on_goto_move)
        self._game_controls.opening_selected.connect(self._on_opening_selected)

    def set_api_client(self, client: ChessAPIClient):
        """Set the API client for game operations."""
        self._api_client = client
        self._coach_chat.set_api_client(client)

    def set_config_service(self, service: ConfigService):
        """Set the config service for settings access."""
        self._config_service = service
        self._update_coach_config()

    def _update_coach_config(self):
        """Update coach chat with current LLM config."""
        if self._config_service:
            config = self._config_service.get_config()
            api_key = self._config_service.get_active_api_key() or ""
            self._coach_chat.set_llm_config(config.llm.provider, api_key)

        # Set context providers
        self._coach_chat.set_context_providers(
            get_fen=self._chess_board.get_fen,
            get_moves=self._chess_board.get_move_history_san
        )

    def _update_ui_state(self):
        """Update UI to reflect current game state."""
        # Update game controls
        turn = self._chess_board.get_current_turn()
        is_check = self._chess_board.is_in_check()
        is_game_over = self._chess_board.is_game_over()
        result = self._chess_board.get_game_result() if is_game_over else ""

        self._game_controls.update_status(turn, is_check, is_game_over, result)
        self._game_controls.update_move_list(self._chess_board.get_move_history_san())

    def _on_move_made(self, move: str):
        """Handle move made on the board."""
        self._state_manager.mark_modified()
        self._update_ui_state()

        # Auto-save if enabled and we have an API client
        if self._state_manager.state.auto_save_enabled and self._api_client:
            self._auto_save()

    def _auto_save(self):
        """Auto-save the current game."""
        if not self._api_client:
            return

        try:
            pgn_data = self._chess_board.get_pgn()
            result = self._chess_board.get_game_result()

            if self._state_manager.current_game_id:
                # Update existing game
                self._api_client.update_game(
                    self._state_manager.current_game_id,
                    pgn_data=pgn_data,
                    result=result
                )
            else:
                # Create new game
                game_data = self._api_client.create_game(
                    pgn_data=pgn_data,
                    result=result,
                    source="desktop"
                )
                self._state_manager.current_game_id = game_data.game_id

            self._state_manager.mark_saved()
            logger.info(f"Auto-saved game {self._state_manager.current_game_id}")

        except APIError as e:
            logger.warning(f"Auto-save failed: {e}")

    def _on_new_game(self):
        """Handle new game request."""
        # Save current game first if modified
        if self._state_manager.is_modified:
            self._auto_save()

        self._chess_board.new_game()
        self._state_manager.reset()
        self._game_controls.clear()
        self._coach_chat.clear_chat()
        self._update_ui_state()

    def _on_save_game(self):
        """Handle save game request."""
        if not self._api_client:
            QMessageBox.warning(
                self,
                "Save Error",
                "API not connected. Cannot save game."
            )
            return

        try:
            pgn_data = self._chess_board.get_pgn()
            result = self._chess_board.get_game_result()

            if self._state_manager.current_game_id:
                self._api_client.update_game(
                    self._state_manager.current_game_id,
                    pgn_data=pgn_data,
                    result=result
                )
                QMessageBox.information(
                    self,
                    "Saved",
                    f"Game {self._state_manager.current_game_id} updated."
                )
            else:
                game_data = self._api_client.create_game(
                    pgn_data=pgn_data,
                    result=result,
                    source="desktop"
                )
                self._state_manager.current_game_id = game_data.game_id
                QMessageBox.information(
                    self,
                    "Saved",
                    f"Game saved with ID: {game_data.game_id}"
                )
                self.game_saved.emit(game_data.game_id)

            self._state_manager.mark_saved()

        except APIError as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save game: {e}")

    def _on_load_pgn(self, pgn_data: str):
        """Handle load PGN request."""
        # Save current game first
        if self._state_manager.is_modified:
            self._auto_save()

        if self._chess_board.load_pgn(pgn_data):
            self._state_manager.reset()
            self._state_manager.mark_modified()
            self._update_ui_state()
            QMessageBox.information(self, "Loaded", "PGN loaded successfully.")
        else:
            QMessageBox.warning(self, "Load Error", "Failed to parse PGN file.")

    def _on_export_pgn(self):
        """Handle export PGN request."""
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Save PGN File",
            "",
            "PGN files (*.pgn);;All files (*)"
        )

        if file_name:
            try:
                pgn_data = self._chess_board.get_pgn()
                with open(file_name, 'w') as f:
                    f.write(pgn_data)
                QMessageBox.information(
                    self,
                    "Exported",
                    f"Game exported to {file_name}"
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Export Error",
                    f"Failed to export PGN: {e}"
                )

    def _on_undo(self):
        """Handle undo request."""
        if self._chess_board.undo_move():
            self._state_manager.mark_modified()
            self._update_ui_state()

    def _on_goto_move(self, move_index: int):
        """Handle goto move request."""
        self._chess_board.goto_move(move_index)
        self._update_ui_state()

    def _on_opening_selected(self, name: str):
        """Handle opening selection."""
        # Save current game first
        if self._state_manager.is_modified:
            self._auto_save()

        if self._state_manager.load_opening(name, self._chess_board.game_service):
            self._chess_board.update()
            self._update_ui_state()

    def load_game(self, game_id: int):
        """Load a game by ID.

        Args:
            game_id: Game ID to load
        """
        if not self._api_client:
            return

        try:
            game_data = self._api_client.get_game(game_id)
            if self._chess_board.load_pgn(game_data.pgn_data):
                self._state_manager.current_game_id = game_id
                self._state_manager.mark_saved()
                self._update_ui_state()
        except APIError as e:
            QMessageBox.critical(self, "Load Error", f"Failed to load game: {e}")

    def refresh_config(self):
        """Refresh configuration (called when settings change)."""
        self._update_coach_config()
