"""Analysis page - game review and analysis interface."""

import logging
from typing import Optional

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QSplitter, QMessageBox
)
from PyQt6.QtCore import Qt

from desktop_client.pages.analysis.components.game_list import GameListWidget
from desktop_client.pages.analysis.components.game_viewer import GameViewerWidget
from desktop_client.pages.analysis.components.analysis_panel import AnalysisPanelWidget
from desktop_client.services.api_client import ChessAPIClient, APIError
from desktop_client.shared.services.config_service import ConfigService

logger = logging.getLogger(__name__)


class AnalysisPage(QWidget):
    """Analysis page for reviewing and analyzing games."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._api_client: Optional[ChessAPIClient] = None
        self._config_service: Optional[ConfigService] = None
        self._current_pgn: Optional[str] = None
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        """Set up the analysis page UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Main splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left panel: Game list
        self._game_list = GameListWidget()
        self._game_list.setMinimumWidth(350)
        splitter.addWidget(self._game_list)

        # Middle panel: Game viewer
        self._game_viewer = GameViewerWidget()
        self._game_viewer.setMinimumWidth(400)
        splitter.addWidget(self._game_viewer)

        # Right panel: Analysis
        self._analysis_panel = AnalysisPanelWidget()
        self._analysis_panel.setMinimumWidth(350)
        splitter.addWidget(self._analysis_panel)

        # Set splitter sizes
        splitter.setSizes([350, 450, 400])

        layout.addWidget(splitter)

    def _connect_signals(self):
        """Connect component signals."""
        self._game_list.game_selected.connect(self._on_game_selected)

    def set_api_client(self, client: ChessAPIClient):
        """Set the API client."""
        self._api_client = client
        self._game_list.set_api_client(client)
        self._analysis_panel.set_api_client(client)

    def set_config_service(self, service: ConfigService):
        """Set the config service."""
        self._config_service = service
        self._update_llm_config()

    def _update_llm_config(self):
        """Update analysis panel with current LLM config."""
        if self._config_service:
            config = self._config_service.get_config()
            api_key = self._config_service.get_active_api_key() or ""
            self._analysis_panel.set_llm_config(config.llm.provider, api_key)

    def _on_game_selected(self, game_id: int):
        """Handle game selection."""
        if not self._api_client:
            return

        try:
            game = self._api_client.get_game(game_id)
            self._current_pgn = game.pgn_data

            # Load into viewer
            self._game_viewer.load_game(game.pgn_data)

            # Set up analysis panel
            self._analysis_panel.set_game(game_id, game.pgn_data)

        except APIError as e:
            QMessageBox.critical(self, "Load Error", f"Failed to load game: {e}")

    def refresh(self):
        """Refresh the page data."""
        self._game_list.load_games()
        self._update_llm_config()

    def on_page_shown(self):
        """Called when page becomes visible."""
        self.refresh()
