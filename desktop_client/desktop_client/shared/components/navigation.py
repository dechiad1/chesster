"""Navigation widget for page switching."""

from enum import Enum
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QFrame
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont


class Page(Enum):
    """Available pages in the application."""
    HOME = "home"
    GAME = "game"
    SETTINGS = "settings"
    ANALYSIS = "analysis"


class NavigationWidget(QWidget):
    """Sidebar navigation widget for switching between pages."""

    page_changed = pyqtSignal(Page)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_page = Page.HOME
        self._buttons: dict[Page, QPushButton] = {}
        self._setup_ui()

    def _setup_ui(self):
        """Set up the navigation UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # App title/logo area
        title_frame = QFrame()
        title_frame.setStyleSheet("""
            QFrame {
                background-color: #1a1a2e;
                padding: 20px;
            }
        """)
        title_layout = QVBoxLayout(title_frame)

        title_label = QLabel("Chesster")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #e0e0e0;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_layout.addWidget(title_label)

        subtitle_label = QLabel("Chess Coach & Analysis")
        subtitle_label.setStyleSheet("color: #888888; font-size: 11px;")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_layout.addWidget(subtitle_label)

        layout.addWidget(title_frame)

        # Navigation buttons
        nav_frame = QFrame()
        nav_frame.setStyleSheet("""
            QFrame {
                background-color: #16213e;
            }
        """)
        nav_layout = QVBoxLayout(nav_frame)
        nav_layout.setContentsMargins(10, 20, 10, 20)
        nav_layout.setSpacing(8)

        # Create navigation buttons
        nav_items = [
            (Page.HOME, "Home", "Return to home screen"),
            (Page.GAME, "Play Game", "Play chess with AI coach"),
            (Page.SETTINGS, "Settings", "Configure your account and preferences"),
            (Page.ANALYSIS, "Analysis", "Review and analyze your games"),
        ]

        for page, label, tooltip in nav_items:
            btn = self._create_nav_button(label, tooltip)
            btn.clicked.connect(lambda checked, p=page: self._on_nav_click(p))
            self._buttons[page] = btn
            nav_layout.addWidget(btn)

        nav_layout.addStretch()
        layout.addWidget(nav_frame, stretch=1)

        # Update button states
        self._update_button_states()

        # Set fixed width for sidebar
        self.setFixedWidth(200)

    def _create_nav_button(self, text: str, tooltip: str) -> QPushButton:
        """Create a styled navigation button."""
        btn = QPushButton(text)
        btn.setToolTip(tooltip)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setMinimumHeight(40)
        btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #b0b0b0;
                border: none;
                border-radius: 6px;
                padding: 10px 15px;
                text-align: left;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #1f3460;
                color: #ffffff;
            }
            QPushButton:pressed {
                background-color: #0f3460;
            }
            QPushButton[selected="true"] {
                background-color: #0f3460;
                color: #ffffff;
                font-weight: bold;
            }
        """)
        return btn

    def _on_nav_click(self, page: Page):
        """Handle navigation button click."""
        if page != self._current_page:
            self._current_page = page
            self._update_button_states()
            self.page_changed.emit(page)

    def _update_button_states(self):
        """Update button visual states based on current page."""
        for page, btn in self._buttons.items():
            is_selected = page == self._current_page
            btn.setProperty("selected", is_selected)
            # Force style refresh
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def set_current_page(self, page: Page):
        """Set the current page without emitting signal.

        Args:
            page: Page to set as current
        """
        self._current_page = page
        self._update_button_states()

    @property
    def current_page(self) -> Page:
        """Get the current page."""
        return self._current_page
