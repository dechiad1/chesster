"""Settings page - configuration management."""

import logging
from typing import Optional

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QScrollArea,
    QFrame
)
from PyQt6.QtCore import pyqtSignal, Qt

from desktop_client.pages.settings.components.account_form import AccountFormWidget
from desktop_client.pages.settings.components.llm_config_form import LLMConfigFormWidget
from desktop_client.pages.settings.components.chesscom_form import ChessComFormWidget
from desktop_client.services.api_client import ChessAPIClient
from desktop_client.shared.services.config_service import ConfigService

logger = logging.getLogger(__name__)


class SettingsPage(QWidget):
    """Settings page with tabbed configuration sections."""

    settings_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._api_client: Optional[ChessAPIClient] = None
        self._config_service: Optional[ConfigService] = None
        self._setup_ui()

    def _setup_ui(self):
        """Set up the settings page UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Tab widget
        self._tabs = QTabWidget()
        self._tabs.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background-color: #0d1520;
            }
            QTabBar::tab {
                background-color: #16213e;
                color: #888888;
                padding: 12px 24px;
                border: none;
                border-bottom: 2px solid transparent;
            }
            QTabBar::tab:selected {
                background-color: #1a2540;
                color: #ffffff;
                border-bottom: 2px solid #4a9eff;
            }
            QTabBar::tab:hover:!selected {
                background-color: #1e2a4a;
                color: #b0b0b0;
            }
        """)

        # Account tab
        account_scroll = QScrollArea()
        account_scroll.setWidgetResizable(True)
        account_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        account_scroll.setStyleSheet("QScrollArea { border: none; background-color: #0d1520; }")

        self._account_form = AccountFormWidget()
        account_scroll.setWidget(self._account_form)
        self._tabs.addTab(account_scroll, "Account")

        # LLM Config tab
        llm_scroll = QScrollArea()
        llm_scroll.setWidgetResizable(True)
        llm_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        llm_scroll.setStyleSheet("QScrollArea { border: none; background-color: #0d1520; }")

        self._llm_form = LLMConfigFormWidget()
        llm_scroll.setWidget(self._llm_form)
        self._tabs.addTab(llm_scroll, "AI Provider")

        # Chess.com tab
        chesscom_scroll = QScrollArea()
        chesscom_scroll.setWidgetResizable(True)
        chesscom_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        chesscom_scroll.setStyleSheet("QScrollArea { border: none; background-color: #0d1520; }")

        self._chesscom_form = ChessComFormWidget()
        chesscom_scroll.setWidget(self._chesscom_form)
        self._tabs.addTab(chesscom_scroll, "Chess.com")

        layout.addWidget(self._tabs)

        # Connect signals
        self._account_form.account_updated.connect(self._on_account_updated)
        self._llm_form.config_saved.connect(self._on_config_saved)
        self._chesscom_form.games_imported.connect(self._on_games_imported)

    def set_api_client(self, client: ChessAPIClient):
        """Set the API client for all forms."""
        self._api_client = client
        self._account_form.set_api_client(client)
        self._chesscom_form.set_api_client(client)

    def set_config_service(self, service: ConfigService):
        """Set the config service for all forms."""
        self._config_service = service
        self._llm_form.set_config_service(service)
        self._chesscom_form.set_config_service(service)

        # Load user if configured
        config = service.get_config()
        if config.account_user_id:
            self._account_form.set_user_id(config.account_user_id)

    def _on_account_updated(self, user_id: int):
        """Handle account update."""
        if self._config_service:
            self._config_service.update_account_user_id(user_id)
        self.settings_changed.emit()

    def _on_config_saved(self):
        """Handle config save."""
        self.settings_changed.emit()

    def _on_games_imported(self, count: int):
        """Handle games imported."""
        logger.info(f"Imported {count} games from Chess.com")
        self.settings_changed.emit()

    def refresh(self):
        """Refresh all forms with current config."""
        if self._config_service:
            self._llm_form.set_config_service(self._config_service)
            self._chesscom_form.set_config_service(self._config_service)
