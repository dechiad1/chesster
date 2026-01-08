"""Chess.com integration form widget."""

import logging
from typing import Optional

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QLabel, QFrame, QMessageBox, QProgressBar
)
from PyQt6.QtCore import pyqtSignal, QThread, pyqtSlot
from PyQt6.QtGui import QFont

from desktop_client.services.api_client import ChessAPIClient, APIError
from desktop_client.shared.services.config_service import ConfigService

logger = logging.getLogger(__name__)


class VerifyWorker(QThread):
    """Worker thread for verifying Chess.com username."""

    success = pyqtSignal(dict)  # profile data
    error = pyqtSignal(str)

    def __init__(self, api_client: ChessAPIClient, username: str):
        super().__init__()
        self.api_client = api_client
        self.username = username

    def run(self):
        try:
            # Fetch games to verify the username exists
            games = self.api_client.fetch_chesscom_games(self.username, count=1)
            self.success.emit({"username": self.username, "verified": True})
        except APIError as e:
            self.error.emit(str(e))
        except Exception as e:
            self.error.emit(f"Verification failed: {e}")


class ImportWorker(QThread):
    """Worker thread for importing Chess.com games."""

    progress = pyqtSignal(int, int)  # current, total
    success = pyqtSignal(int)  # number of games imported
    error = pyqtSignal(str)

    def __init__(self, api_client: ChessAPIClient, username: str, count: int = 50):
        super().__init__()
        self.api_client = api_client
        self.username = username
        self.count = count

    def run(self):
        try:
            games = self.api_client.fetch_chesscom_games(self.username, self.count)
            imported = 0

            for i, game in enumerate(games):
                try:
                    # Import each game to the local database
                    self.api_client.import_game_pgn(game.pgn)
                    imported += 1
                    self.progress.emit(i + 1, len(games))
                except APIError:
                    pass  # Skip games that fail to import

            self.success.emit(imported)
        except APIError as e:
            self.error.emit(str(e))
        except Exception as e:
            self.error.emit(f"Import failed: {e}")


class ChessComFormWidget(QWidget):
    """Form for Chess.com integration settings."""

    username_verified = pyqtSignal(str)
    games_imported = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._api_client: Optional[ChessAPIClient] = None
        self._config_service: Optional[ConfigService] = None
        self._verify_worker: Optional[VerifyWorker] = None
        self._import_worker: Optional[ImportWorker] = None
        self._setup_ui()

    def _setup_ui(self):
        """Set up the form UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header
        header = QFrame()
        header.setStyleSheet("background-color: #1a1a2e;")
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(20, 15, 20, 15)

        title = QLabel("Chess.com Integration")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #ffffff;")
        header_layout.addWidget(title)

        subtitle = QLabel("Connect your Chess.com account to import games")
        subtitle.setStyleSheet("color: #888888; font-size: 12px;")
        header_layout.addWidget(subtitle)

        layout.addWidget(header)

        # Form
        form_frame = QFrame()
        form_frame.setStyleSheet("background-color: #16213e;")
        form_layout = QVBoxLayout(form_frame)
        form_layout.setContentsMargins(20, 20, 20, 20)
        form_layout.setSpacing(15)

        # Username input
        username_label = QLabel("Chess.com Username")
        username_label.setStyleSheet("color: #ffffff; font-weight: bold; font-size: 13px;")
        form_layout.addWidget(username_label)

        username_row = QHBoxLayout()
        username_row.setSpacing(10)

        self._username_input = QLineEdit()
        self._username_input.setPlaceholderText("Enter your Chess.com username")
        self._username_input.setStyleSheet("""
            QLineEdit {
                background-color: #253156;
                color: #ffffff;
                border: 1px solid #3a4a6a;
                border-radius: 6px;
                padding: 10px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border-color: #4a9eff;
            }
        """)
        username_row.addWidget(self._username_input, stretch=1)

        self._verify_btn = QPushButton("Verify")
        self._verify_btn.setStyleSheet("""
            QPushButton {
                background-color: #17a2b8;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #138496;
            }
            QPushButton:disabled {
                background-color: #3a4a5a;
                color: #888888;
            }
        """)
        self._verify_btn.clicked.connect(self._on_verify)
        username_row.addWidget(self._verify_btn)

        form_layout.addLayout(username_row)

        # Status label
        self._status_label = QLabel("")
        self._status_label.setStyleSheet("color: #888888; font-size: 12px;")
        form_layout.addWidget(self._status_label)

        # Import section
        import_label = QLabel("Import Games")
        import_label.setStyleSheet("color: #ffffff; font-weight: bold; font-size: 13px; margin-top: 10px;")
        form_layout.addWidget(import_label)

        import_desc = QLabel(
            "Import your recent games from Chess.com to analyze them locally. "
            "This will fetch your game history and store it in the app."
        )
        import_desc.setWordWrap(True)
        import_desc.setStyleSheet("color: #888888; font-size: 12px;")
        form_layout.addWidget(import_desc)

        import_row = QHBoxLayout()
        import_row.setSpacing(10)

        self._import_btn = QPushButton("Import Last 50 Games")
        self._import_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:disabled {
                background-color: #3a4a5a;
                color: #888888;
            }
        """)
        self._import_btn.clicked.connect(self._on_import)
        import_row.addWidget(self._import_btn)

        import_row.addStretch()
        form_layout.addLayout(import_row)

        # Progress bar
        self._progress_bar = QProgressBar()
        self._progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #253156;
                border: 1px solid #3a4a6a;
                border-radius: 4px;
                text-align: center;
                color: #ffffff;
            }
            QProgressBar::chunk {
                background-color: #4a9eff;
                border-radius: 3px;
            }
        """)
        self._progress_bar.setVisible(False)
        form_layout.addWidget(self._progress_bar)

        # Import status
        self._import_status = QLabel("")
        self._import_status.setStyleSheet("color: #888888; font-size: 12px;")
        form_layout.addWidget(self._import_status)

        layout.addWidget(form_frame)

        # Save button
        save_frame = QFrame()
        save_frame.setStyleSheet("background-color: #16213e;")
        save_layout = QHBoxLayout(save_frame)
        save_layout.setContentsMargins(20, 10, 20, 20)

        save_layout.addStretch()

        self._save_btn = QPushButton("Save Username")
        self._save_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a9eff;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 24px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3a8eef;
            }
        """)
        self._save_btn.clicked.connect(self._on_save)
        save_layout.addWidget(self._save_btn)

        layout.addWidget(save_frame)
        layout.addStretch()

    def set_api_client(self, client: ChessAPIClient):
        """Set the API client."""
        self._api_client = client

    def set_config_service(self, service: ConfigService):
        """Set the config service and load current config."""
        self._config_service = service
        self._load_config()

    def _load_config(self):
        """Load current configuration."""
        if not self._config_service:
            return

        config = self._config_service.get_config()
        if config.chesscom_username:
            self._username_input.setText(config.chesscom_username)
            self._status_label.setText(f"Current username: {config.chesscom_username}")
            self._status_label.setStyleSheet("color: #28a745; font-size: 12px;")

    def _on_verify(self):
        """Verify the Chess.com username."""
        username = self._username_input.text().strip()
        if not username:
            QMessageBox.warning(self, "Input Required", "Please enter a Chess.com username.")
            return

        if not self._api_client:
            QMessageBox.warning(self, "Connection Error", "API not connected.")
            return

        self._verify_btn.setEnabled(False)
        self._status_label.setText("Verifying...")
        self._status_label.setStyleSheet("color: #ffc107; font-size: 12px;")

        self._verify_worker = VerifyWorker(self._api_client, username)
        self._verify_worker.success.connect(self._on_verify_success)
        self._verify_worker.error.connect(self._on_verify_error)
        self._verify_worker.start()

    @pyqtSlot(dict)
    def _on_verify_success(self, data: dict):
        """Handle successful verification."""
        self._verify_btn.setEnabled(True)
        self._status_label.setText(f"Username '{data['username']}' verified!")
        self._status_label.setStyleSheet("color: #28a745; font-size: 12px;")
        self.username_verified.emit(data['username'])

    @pyqtSlot(str)
    def _on_verify_error(self, error: str):
        """Handle verification error."""
        self._verify_btn.setEnabled(True)
        self._status_label.setText(f"Verification failed: {error}")
        self._status_label.setStyleSheet("color: #dc3545; font-size: 12px;")

    def _on_import(self):
        """Import games from Chess.com."""
        username = self._username_input.text().strip()
        if not username:
            QMessageBox.warning(self, "Input Required", "Please enter a Chess.com username first.")
            return

        if not self._api_client:
            QMessageBox.warning(self, "Connection Error", "API not connected.")
            return

        self._import_btn.setEnabled(False)
        self._progress_bar.setVisible(True)
        self._progress_bar.setValue(0)
        self._import_status.setText("Fetching games...")

        self._import_worker = ImportWorker(self._api_client, username, count=50)
        self._import_worker.progress.connect(self._on_import_progress)
        self._import_worker.success.connect(self._on_import_success)
        self._import_worker.error.connect(self._on_import_error)
        self._import_worker.start()

    @pyqtSlot(int, int)
    def _on_import_progress(self, current: int, total: int):
        """Handle import progress update."""
        self._progress_bar.setMaximum(total)
        self._progress_bar.setValue(current)
        self._import_status.setText(f"Importing game {current} of {total}...")

    @pyqtSlot(int)
    def _on_import_success(self, count: int):
        """Handle successful import."""
        self._import_btn.setEnabled(True)
        self._progress_bar.setVisible(False)
        self._import_status.setText(f"Successfully imported {count} games!")
        self._import_status.setStyleSheet("color: #28a745; font-size: 12px;")
        self.games_imported.emit(count)

    @pyqtSlot(str)
    def _on_import_error(self, error: str):
        """Handle import error."""
        self._import_btn.setEnabled(True)
        self._progress_bar.setVisible(False)
        self._import_status.setText(f"Import failed: {error}")
        self._import_status.setStyleSheet("color: #dc3545; font-size: 12px;")

    def _on_save(self):
        """Save the username to config."""
        if not self._config_service:
            QMessageBox.warning(self, "Save Error", "Configuration service not available.")
            return

        username = self._username_input.text().strip()
        self._config_service.update_chesscom_username(username)

        QMessageBox.information(
            self,
            "Saved",
            f"Chess.com username saved: {username}" if username else "Chess.com username cleared."
        )

    def get_username(self) -> str:
        """Get the current username."""
        return self._username_input.text().strip()
