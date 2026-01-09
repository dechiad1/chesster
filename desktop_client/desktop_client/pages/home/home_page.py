"""Home page - main navigation hub."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QGridLayout
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont

from desktop_client.shared.components.navigation import Page


class HomePageCard(QFrame):
    """Clickable card for navigation."""

    clicked = pyqtSignal()

    def __init__(self, title: str, description: str, icon_text: str, parent=None):
        super().__init__(parent)
        self._setup_ui(title, description, icon_text)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def _setup_ui(self, title: str, description: str, icon_text: str):
        """Set up the card UI."""
        self.setStyleSheet("""
            HomePageCard {
                background-color: #1e2746;
                border-radius: 12px;
                border: 1px solid #2a3a5a;
            }
            HomePageCard:hover {
                background-color: #253156;
                border-color: #3a5a8a;
            }
        """)
        self.setMinimumSize(280, 180)
        self.setMaximumSize(320, 200)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # Icon
        icon_label = QLabel(icon_text)
        icon_font = QFont()
        icon_font.setPointSize(36)
        icon_label.setFont(icon_font)
        icon_label.setStyleSheet("color: #4a9eff;")
        layout.addWidget(icon_label)

        # Title
        title_label = QLabel(title)
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #ffffff;")
        layout.addWidget(title_label)

        # Description
        desc_label = QLabel(description)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #a0a0a0; font-size: 12px;")
        layout.addWidget(desc_label)

        layout.addStretch()

    def mousePressEvent(self, event):
        """Handle mouse press."""
        self.clicked.emit()
        super().mousePressEvent(event)


class HomePage(QWidget):
    """Home page with navigation cards."""

    navigate_to = pyqtSignal(Page)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """Set up the home page UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(30)

        # Header
        header_layout = QVBoxLayout()
        header_layout.setSpacing(8)

        welcome_label = QLabel("Welcome to Chesster")
        welcome_font = QFont()
        welcome_font.setPointSize(28)
        welcome_font.setBold(True)
        welcome_label.setFont(welcome_font)
        welcome_label.setStyleSheet("color: #ffffff;")
        header_layout.addWidget(welcome_label)

        subtitle_label = QLabel("Your personal chess coach and game analyzer")
        subtitle_label.setStyleSheet("color: #888888; font-size: 14px;")
        header_layout.addWidget(subtitle_label)

        layout.addLayout(header_layout)

        # Cards grid
        cards_widget = QWidget()
        cards_layout = QGridLayout(cards_widget)
        cards_layout.setSpacing(20)

        # Game card
        game_card = HomePageCard(
            "Play Game",
            "Play chess against yourself or practice with an AI coach by your side.",
            "♟"
        )
        game_card.clicked.connect(lambda: self.navigate_to.emit(Page.GAME))
        cards_layout.addWidget(game_card, 0, 0)

        # Settings card
        settings_card = HomePageCard(
            "Settings",
            "Configure your account, LLM provider, and Chess.com integration.",
            "⚙"
        )
        settings_card.clicked.connect(lambda: self.navigate_to.emit(Page.SETTINGS))
        cards_layout.addWidget(settings_card, 0, 1)

        # Analysis card
        analysis_card = HomePageCard(
            "Analysis",
            "Review your games and get AI-powered insights on mistakes and improvements.",
            "📊"
        )
        analysis_card.clicked.connect(lambda: self.navigate_to.emit(Page.ANALYSIS))
        cards_layout.addWidget(analysis_card, 1, 0)

        # Quick stats placeholder
        stats_card = HomePageCard(
            "Quick Stats",
            "Coming soon: View your recent performance at a glance.",
            "📈"
        )
        stats_card.setEnabled(False)
        stats_card.setStyleSheet("""
            HomePageCard {
                background-color: #1a2030;
                border-radius: 12px;
                border: 1px solid #252535;
                opacity: 0.6;
            }
        """)
        cards_layout.addWidget(stats_card, 1, 1)

        layout.addWidget(cards_widget)
        layout.addStretch()

        # Footer
        footer_label = QLabel("Tip: Configure your LLM settings to enable AI coaching features")
        footer_label.setStyleSheet("color: #666666; font-size: 11px;")
        footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(footer_label)
