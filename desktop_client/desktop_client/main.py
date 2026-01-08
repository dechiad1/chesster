"""Main entry point for the Chesster desktop application."""

import sys
import logging
from typing import Optional

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout,
    QStackedWidget, QStatusBar, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon, QShortcut, QKeySequence

from desktop_client.shared.components.navigation import NavigationWidget, Page
from desktop_client.shared.services.config_service import ConfigService
from desktop_client.services.api_client import ChessAPIClient
from desktop_client.pages.home.home_page import HomePage
from desktop_client.pages.game.game_page import GamePage
from desktop_client.pages.settings.settings_page import SettingsPage
from desktop_client.pages.analysis.analysis_page import AnalysisPage

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ChessterApp(QMainWindow):
    """Main application window with multi-page navigation."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chesster - Chess Coach & Analysis")

        # Services
        self._config_service = ConfigService()
        self._api_client = ChessAPIClient()
        self._api_connected = False

        # Set up UI
        self._setup_ui()
        self._setup_shortcuts()

        # Check API connection
        self._check_api_connection()

        # Apply dark theme
        self._apply_theme()

    def _setup_ui(self):
        """Set up the main UI."""
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)

        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Navigation sidebar
        self._navigation = NavigationWidget()
        self._navigation.page_changed.connect(self._on_page_changed)
        layout.addWidget(self._navigation)

        # Page stack
        self._page_stack = QStackedWidget()
        self._page_stack.setStyleSheet("background-color: #0d1520;")

        # Create pages
        self._home_page = HomePage()
        self._home_page.navigate_to.connect(self._navigate_to)

        self._game_page = GamePage()
        self._game_page.set_api_client(self._api_client)
        self._game_page.set_config_service(self._config_service)

        self._settings_page = SettingsPage()
        self._settings_page.set_api_client(self._api_client)
        self._settings_page.set_config_service(self._config_service)
        self._settings_page.settings_changed.connect(self._on_settings_changed)

        self._analysis_page = AnalysisPage()
        self._analysis_page.set_api_client(self._api_client)
        self._analysis_page.set_config_service(self._config_service)

        # Add pages to stack
        self._page_stack.addWidget(self._home_page)      # Index 0
        self._page_stack.addWidget(self._game_page)      # Index 1
        self._page_stack.addWidget(self._settings_page)  # Index 2
        self._page_stack.addWidget(self._analysis_page)  # Index 3

        layout.addWidget(self._page_stack, stretch=1)

        # Status bar
        self._status_bar = QStatusBar()
        self._status_bar.setStyleSheet("""
            QStatusBar {
                background-color: #1a1a2e;
                color: #888888;
                border-top: 1px solid #2a2a4e;
            }
        """)
        self.setStatusBar(self._status_bar)
        self._update_status_bar()

    def _setup_shortcuts(self):
        """Set up keyboard shortcuts."""
        # Quit
        quit_shortcut = QShortcut(QKeySequence("Ctrl+Q"), self)
        quit_shortcut.activated.connect(self.close)

        quit_shortcut_w = QShortcut(QKeySequence("Ctrl+W"), self)
        quit_shortcut_w.activated.connect(self.close)

        # Navigation shortcuts
        home_shortcut = QShortcut(QKeySequence("Ctrl+1"), self)
        home_shortcut.activated.connect(lambda: self._navigate_to(Page.HOME))

        game_shortcut = QShortcut(QKeySequence("Ctrl+2"), self)
        game_shortcut.activated.connect(lambda: self._navigate_to(Page.GAME))

        settings_shortcut = QShortcut(QKeySequence("Ctrl+3"), self)
        settings_shortcut.activated.connect(lambda: self._navigate_to(Page.SETTINGS))

        analysis_shortcut = QShortcut(QKeySequence("Ctrl+4"), self)
        analysis_shortcut.activated.connect(lambda: self._navigate_to(Page.ANALYSIS))

    def _apply_theme(self):
        """Apply the dark theme."""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0d1520;
            }
            QToolTip {
                background-color: #1a1a2e;
                color: #ffffff;
                border: 1px solid #3a3a5e;
                padding: 4px;
            }
            QScrollBar:vertical {
                background-color: #16213e;
                width: 12px;
                margin: 0;
            }
            QScrollBar::handle:vertical {
                background-color: #3a4a6a;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #4a5a7a;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0;
            }
            QScrollBar:horizontal {
                background-color: #16213e;
                height: 12px;
                margin: 0;
            }
            QScrollBar::handle:horizontal {
                background-color: #3a4a6a;
                border-radius: 6px;
                min-width: 20px;
            }
            QScrollBar::handle:horizontal:hover {
                background-color: #4a5a7a;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0;
            }
        """)

    def _check_api_connection(self):
        """Check if the API server is available."""
        try:
            self._api_connected = self._api_client.health_check()
            if not self._api_connected:
                logger.warning("API server not available")
                QMessageBox.warning(
                    self,
                    "API Connection",
                    "Could not connect to the API server.\n"
                    "Make sure the server is running at http://localhost:8000\n\n"
                    "You can still use the app, but some features will be limited."
                )
        except Exception as e:
            logger.error(f"API connection check failed: {e}")
            self._api_connected = False

        self._update_status_bar()

    def _update_status_bar(self):
        """Update the status bar."""
        api_status = "API: Connected" if self._api_connected else "API: Disconnected"
        config = self._config_service.get_config()
        llm_status = f"LLM: {config.llm.provider.title()}"

        if self._config_service.is_llm_configured():
            llm_status += " (configured)"
        else:
            llm_status += " (not configured)"

        self._status_bar.showMessage(f"{api_status}  |  {llm_status}")

    def _on_page_changed(self, page: Page):
        """Handle page change from navigation."""
        self._navigate_to(page)

    def _navigate_to(self, page: Page):
        """Navigate to a specific page."""
        page_index = {
            Page.HOME: 0,
            Page.GAME: 1,
            Page.SETTINGS: 2,
            Page.ANALYSIS: 3
        }.get(page, 0)

        self._page_stack.setCurrentIndex(page_index)
        self._navigation.set_current_page(page)

        # Notify pages when they become visible
        if page == Page.ANALYSIS:
            self._analysis_page.on_page_shown()
        elif page == Page.GAME:
            self._game_page.refresh_config()

    def _on_settings_changed(self):
        """Handle settings change."""
        self._update_status_bar()
        # Refresh config in other pages
        self._game_page.refresh_config()
        self._analysis_page.set_config_service(self._config_service)

    def closeEvent(self, event):
        """Handle application close."""
        if self._api_client:
            self._api_client.close()
        event.accept()


def main():
    """Main entry point."""
    app = QApplication(sys.argv)
    app.setApplicationName("Chesster")
    app.setApplicationDisplayName("Chesster")

    # Set app icon if available
    try:
        app.setWindowIcon(QIcon('./resources/chess-finesse.png'))
    except Exception:
        pass

    # Create and show main window
    window = ChessterApp()
    window.resize(1400, 800)
    window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
