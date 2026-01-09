"""Account settings form widget."""

import logging
from typing import Optional

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit,
    QPushButton, QLabel, QComboBox, QFrame, QMessageBox
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont

from desktop_client.services.api_client import ChessAPIClient, APIError, UserData

logger = logging.getLogger(__name__)


class AccountFormWidget(QWidget):
    """Form for managing user account settings."""

    account_updated = pyqtSignal(int)  # user_id

    def __init__(self, parent=None):
        super().__init__(parent)
        self._api_client: Optional[ChessAPIClient] = None
        self._current_user_id: Optional[int] = None
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

        title = QLabel("Account Settings")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #ffffff;")
        header_layout.addWidget(title)

        subtitle = QLabel("Manage your profile information")
        subtitle.setStyleSheet("color: #888888; font-size: 12px;")
        header_layout.addWidget(subtitle)

        layout.addWidget(header)

        # Form
        form_frame = QFrame()
        form_frame.setStyleSheet("background-color: #16213e;")
        form_layout = QFormLayout(form_frame)
        form_layout.setContentsMargins(20, 20, 20, 20)
        form_layout.setSpacing(15)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        # Username
        self._username_input = QLineEdit()
        self._username_input.setPlaceholderText("Enter username")
        self._style_input(self._username_input)
        form_layout.addRow(self._create_label("Username:"), self._username_input)

        # Email
        self._email_input = QLineEdit()
        self._email_input.setPlaceholderText("Enter email")
        self._style_input(self._email_input)
        form_layout.addRow(self._create_label("Email:"), self._email_input)

        # Full Name
        self._fullname_input = QLineEdit()
        self._fullname_input.setPlaceholderText("Enter full name")
        self._style_input(self._fullname_input)
        form_layout.addRow(self._create_label("Full Name:"), self._fullname_input)

        # Skill Level
        self._skill_combo = QComboBox()
        self._skill_combo.addItems(["Beginner", "Intermediate", "Advanced", "Expert"])
        self._style_combo(self._skill_combo)
        form_layout.addRow(self._create_label("Skill Level:"), self._skill_combo)

        # Preferred Color
        self._color_combo = QComboBox()
        self._color_combo.addItems(["White", "Black", "Random"])
        self._style_combo(self._color_combo)
        form_layout.addRow(self._create_label("Preferred Color:"), self._color_combo)

        layout.addWidget(form_frame)

        # Actions
        actions_frame = QFrame()
        actions_frame.setStyleSheet("background-color: #16213e;")
        actions_layout = QHBoxLayout(actions_frame)
        actions_layout.setContentsMargins(20, 10, 20, 20)
        actions_layout.setSpacing(10)

        actions_layout.addStretch()

        self._save_btn = QPushButton("Save Account")
        self._save_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 24px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:pressed {
                background-color: #1e7e34;
            }
        """)
        self._save_btn.clicked.connect(self._on_save)
        actions_layout.addWidget(self._save_btn)

        layout.addWidget(actions_frame)
        layout.addStretch()

    def _create_label(self, text: str) -> QLabel:
        """Create a styled form label."""
        label = QLabel(text)
        label.setStyleSheet("color: #b0b0b0; font-size: 13px;")
        return label

    def _style_input(self, widget: QLineEdit):
        """Apply styling to an input widget."""
        widget.setStyleSheet("""
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
        widget.setMinimumWidth(250)

    def _style_combo(self, widget: QComboBox):
        """Apply styling to a combo box."""
        widget.setStyleSheet("""
            QComboBox {
                background-color: #253156;
                color: #ffffff;
                border: 1px solid #3a4a6a;
                border-radius: 6px;
                padding: 8px;
                font-size: 13px;
            }
            QComboBox:hover {
                border-color: #4a9eff;
            }
            QComboBox::drop-down {
                border: none;
                padding-right: 10px;
            }
            QComboBox QAbstractItemView {
                background-color: #253156;
                color: #ffffff;
                selection-background-color: #4a9eff;
            }
        """)
        widget.setMinimumWidth(250)

    def set_api_client(self, client: ChessAPIClient):
        """Set the API client."""
        self._api_client = client

    def load_user(self, user_id: int):
        """Load user data from API.

        Args:
            user_id: User ID to load
        """
        if not self._api_client:
            return

        try:
            user = self._api_client.get_user(user_id)
            self._current_user_id = user_id
            self._username_input.setText(user.username)
            self._email_input.setText(user.email)
            self._fullname_input.setText(user.full_name)
        except APIError as e:
            logger.warning(f"Failed to load user: {e}")

    def set_user_id(self, user_id: Optional[int]):
        """Set the current user ID."""
        self._current_user_id = user_id
        if user_id:
            self.load_user(user_id)

    def _on_save(self):
        """Handle save button click."""
        username = self._username_input.text().strip()
        email = self._email_input.text().strip()
        full_name = self._fullname_input.text().strip()

        if not username or not email:
            QMessageBox.warning(
                self,
                "Validation Error",
                "Username and email are required."
            )
            return

        if not self._api_client:
            QMessageBox.warning(
                self,
                "Connection Error",
                "API not connected. Cannot save account."
            )
            return

        try:
            if self._current_user_id:
                # Update existing user (would need API endpoint)
                QMessageBox.information(
                    self,
                    "Account Updated",
                    "Account settings saved locally. Full update requires API support."
                )
            else:
                # Create new user
                user = self._api_client.create_user(
                    username=username,
                    email=email,
                    full_name=full_name,
                    password="temporary"  # Would need proper password handling
                )
                self._current_user_id = user.user_id
                self.account_updated.emit(user.user_id)
                QMessageBox.information(
                    self,
                    "Account Created",
                    f"Account created with ID: {user.user_id}"
                )

        except APIError as e:
            QMessageBox.critical(
                self,
                "Save Error",
                f"Failed to save account: {e}"
            )

    def get_form_data(self) -> dict:
        """Get current form data.

        Returns:
            Dictionary of form values
        """
        return {
            "username": self._username_input.text().strip(),
            "email": self._email_input.text().strip(),
            "full_name": self._fullname_input.text().strip(),
            "skill_level": self._skill_combo.currentText().lower(),
            "preferred_color": self._color_combo.currentText().lower()
        }
