"""Coach chat widget for interacting with the LLM coach."""

import logging
from typing import Optional, Callable

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit,
    QPushButton, QLabel, QFrame, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, pyqtSlot
from PyQt6.QtGui import QFont, QTextCursor

from desktop_client.services.api_client import ChessAPIClient, APIError

logger = logging.getLogger(__name__)


class CoachChatWorker(QThread):
    """Worker thread for coach chat API calls."""

    response_received = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(
        self,
        api_client: ChessAPIClient,
        message: str,
        fen: str,
        move_history: list[str],
        provider: str,
        api_key: str
    ):
        super().__init__()
        self.api_client = api_client
        self.message = message
        self.fen = fen
        self.move_history = move_history
        self.provider = provider
        self.api_key = api_key

    def run(self):
        """Run the chat request in background."""
        try:
            response = self.api_client.coach_chat(
                message=self.message,
                fen=self.fen,
                move_history=self.move_history,
                provider=self.provider,
                api_key=self.api_key
            )
            self.response_received.emit(response)
        except APIError as e:
            self.error_occurred.emit(str(e))
        except Exception as e:
            self.error_occurred.emit(f"Unexpected error: {e}")


class ChatMessage(QFrame):
    """Single chat message widget."""

    def __init__(self, text: str, is_user: bool, parent=None):
        super().__init__(parent)
        self._setup_ui(text, is_user)

    def _setup_ui(self, text: str, is_user: bool):
        """Set up the message UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)

        # Sender label
        sender = "You" if is_user else "Coach"
        sender_label = QLabel(sender)
        sender_font = QFont()
        sender_font.setBold(True)
        sender_font.setPointSize(10)
        sender_label.setFont(sender_font)

        # Message text
        message_label = QLabel(text)
        message_label.setWordWrap(True)
        message_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )

        if is_user:
            self.setStyleSheet("""
                ChatMessage {
                    background-color: #0f3460;
                    border-radius: 8px;
                    margin-left: 40px;
                }
            """)
            sender_label.setStyleSheet("color: #6eb5ff;")
            message_label.setStyleSheet("color: #e0e0e0;")
        else:
            self.setStyleSheet("""
                ChatMessage {
                    background-color: #1e2746;
                    border-radius: 8px;
                    margin-right: 40px;
                }
            """)
            sender_label.setStyleSheet("color: #5cb85c;")
            message_label.setStyleSheet("color: #d0d0d0;")

        layout.addWidget(sender_label)
        layout.addWidget(message_label)


class CoachChatWidget(QWidget):
    """Chat widget for interacting with the chess coach."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._api_client: Optional[ChessAPIClient] = None
        self._get_fen: Optional[Callable[[], str]] = None
        self._get_moves: Optional[Callable[[], list[str]]] = None
        self._provider: str = "anthropic"
        self._api_key: str = ""
        self._chat_worker: Optional[CoachChatWorker] = None
        self._messages: list[dict] = []

        self._setup_ui()

    def _setup_ui(self):
        """Set up the chat UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header
        header = QFrame()
        header.setStyleSheet("background-color: #1a1a2e; padding: 10px;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(15, 10, 15, 10)

        title_label = QLabel("Chess Coach")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #ffffff;")
        header_layout.addWidget(title_label)

        self._status_label = QLabel("Ready")
        self._status_label.setStyleSheet("color: #888888; font-size: 11px;")
        header_layout.addWidget(self._status_label, alignment=Qt.AlignmentFlag.AlignRight)

        layout.addWidget(header)

        # Chat area
        self._chat_scroll = QScrollArea()
        self._chat_scroll.setWidgetResizable(True)
        self._chat_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._chat_scroll.setStyleSheet("""
            QScrollArea {
                background-color: #16213e;
                border: none;
            }
        """)

        self._chat_container = QWidget()
        self._chat_layout = QVBoxLayout(self._chat_container)
        self._chat_layout.setContentsMargins(10, 10, 10, 10)
        self._chat_layout.setSpacing(10)
        self._chat_layout.addStretch()

        self._chat_scroll.setWidget(self._chat_container)
        layout.addWidget(self._chat_scroll, stretch=1)

        # Welcome message
        self._add_coach_message(
            "Hello! I'm your chess coach. Ask me about the position, "
            "strategy, tactics, or any chess concepts you'd like to understand better."
        )

        # Input area
        input_frame = QFrame()
        input_frame.setStyleSheet("background-color: #1a1a2e;")
        input_layout = QHBoxLayout(input_frame)
        input_layout.setContentsMargins(10, 10, 10, 10)
        input_layout.setSpacing(8)

        self._message_input = QLineEdit()
        self._message_input.setPlaceholderText("Ask your coach a question...")
        self._message_input.setStyleSheet("""
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
        self._message_input.returnPressed.connect(self._send_message)
        input_layout.addWidget(self._message_input, stretch=1)

        self._send_btn = QPushButton("Send")
        self._send_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a9eff;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3a8eef;
            }
            QPushButton:pressed {
                background-color: #2a7edf;
            }
            QPushButton:disabled {
                background-color: #3a4a5a;
                color: #888888;
            }
        """)
        self._send_btn.clicked.connect(self._send_message)
        input_layout.addWidget(self._send_btn)

        layout.addWidget(input_frame)

    def set_api_client(self, client: ChessAPIClient):
        """Set the API client for chat requests."""
        self._api_client = client

    def set_context_providers(
        self,
        get_fen: Callable[[], str],
        get_moves: Callable[[], list[str]]
    ):
        """Set functions to get current game context.

        Args:
            get_fen: Function that returns current FEN
            get_moves: Function that returns move history
        """
        self._get_fen = get_fen
        self._get_moves = get_moves

    def set_llm_config(self, provider: str, api_key: str):
        """Set the LLM configuration.

        Args:
            provider: LLM provider name
            api_key: API key for the provider
        """
        self._provider = provider
        self._api_key = api_key

    def _send_message(self):
        """Send a message to the coach."""
        message = self._message_input.text().strip()
        if not message:
            return

        if not self._api_client:
            self._add_coach_message(
                "Chat is not available. Please check your API connection."
            )
            return

        if not self._api_key:
            self._add_coach_message(
                "Please configure your LLM API key in Settings to chat with the coach."
            )
            return

        # Add user message to chat
        self._add_user_message(message)
        self._message_input.clear()

        # Get game context
        fen = self._get_fen() if self._get_fen else ""
        moves = self._get_moves() if self._get_moves else []

        # Start worker thread
        self._set_loading(True)
        self._chat_worker = CoachChatWorker(
            self._api_client,
            message,
            fen,
            moves,
            self._provider,
            self._api_key
        )
        self._chat_worker.response_received.connect(self._on_response)
        self._chat_worker.error_occurred.connect(self._on_error)
        self._chat_worker.start()

    def _add_user_message(self, text: str):
        """Add a user message to the chat."""
        self._messages.append({"role": "user", "content": text})
        message_widget = ChatMessage(text, is_user=True)
        # Insert before the stretch
        self._chat_layout.insertWidget(self._chat_layout.count() - 1, message_widget)
        self._scroll_to_bottom()

    def _add_coach_message(self, text: str):
        """Add a coach message to the chat."""
        self._messages.append({"role": "coach", "content": text})
        message_widget = ChatMessage(text, is_user=False)
        # Insert before the stretch
        self._chat_layout.insertWidget(self._chat_layout.count() - 1, message_widget)
        self._scroll_to_bottom()

    def _scroll_to_bottom(self):
        """Scroll chat to the bottom."""
        scrollbar = self._chat_scroll.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def _set_loading(self, loading: bool):
        """Set loading state."""
        self._send_btn.setEnabled(not loading)
        self._message_input.setEnabled(not loading)
        self._status_label.setText("Thinking..." if loading else "Ready")

    @pyqtSlot(str)
    def _on_response(self, response: str):
        """Handle coach response."""
        self._set_loading(False)
        self._add_coach_message(response)

    @pyqtSlot(str)
    def _on_error(self, error: str):
        """Handle error."""
        self._set_loading(False)
        self._add_coach_message(f"Sorry, I encountered an error: {error}")

    def clear_chat(self):
        """Clear the chat history."""
        self._messages.clear()
        # Remove all messages except the stretch
        while self._chat_layout.count() > 1:
            item = self._chat_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        # Add welcome message back
        self._add_coach_message(
            "Chat cleared. I'm ready to help with your new game!"
        )
