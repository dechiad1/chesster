"""LLM configuration form widget."""

import logging
from typing import Optional

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit,
    QPushButton, QLabel, QRadioButton, QButtonGroup, QFrame,
    QMessageBox
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont

from desktop_client.shared.services.config_service import ConfigService, LLMConfig

logger = logging.getLogger(__name__)


class LLMConfigFormWidget(QWidget):
    """Form for configuring LLM provider settings."""

    config_saved = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._config_service: Optional[ConfigService] = None
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

        title = QLabel("LLM Configuration")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #ffffff;")
        header_layout.addWidget(title)

        subtitle = QLabel("Configure your AI provider for coaching and analysis")
        subtitle.setStyleSheet("color: #888888; font-size: 12px;")
        header_layout.addWidget(subtitle)

        layout.addWidget(header)

        # Provider selection
        provider_frame = QFrame()
        provider_frame.setStyleSheet("background-color: #16213e;")
        provider_layout = QVBoxLayout(provider_frame)
        provider_layout.setContentsMargins(20, 20, 20, 15)
        provider_layout.setSpacing(12)

        provider_label = QLabel("Select Provider")
        provider_label.setStyleSheet("color: #ffffff; font-weight: bold; font-size: 14px;")
        provider_layout.addWidget(provider_label)

        # Radio buttons for providers
        self._provider_group = QButtonGroup(self)

        providers = [
            ("anthropic", "Anthropic (Claude)", "Best for chess coaching and analysis"),
            ("openai", "OpenAI (GPT)", "Alternative high-quality option"),
            ("gemini", "Google (Gemini)", "Google's AI offering"),
            ("local", "Local Model", "Use a locally running model (Ollama, etc.)")
        ]

        for provider_id, name, description in providers:
            radio_widget = QWidget()
            radio_layout = QVBoxLayout(radio_widget)
            radio_layout.setContentsMargins(0, 0, 0, 0)
            radio_layout.setSpacing(2)

            radio = QRadioButton(name)
            radio.setProperty("provider_id", provider_id)
            radio.setStyleSheet("""
                QRadioButton {
                    color: #e0e0e0;
                    font-size: 13px;
                }
                QRadioButton::indicator {
                    width: 16px;
                    height: 16px;
                }
            """)
            self._provider_group.addButton(radio)
            radio_layout.addWidget(radio)

            desc_label = QLabel(description)
            desc_label.setStyleSheet("color: #888888; font-size: 11px; margin-left: 24px;")
            radio_layout.addWidget(desc_label)

            provider_layout.addWidget(radio_widget)

        layout.addWidget(provider_frame)

        # API Key inputs
        keys_frame = QFrame()
        keys_frame.setStyleSheet("background-color: #16213e;")
        keys_layout = QVBoxLayout(keys_frame)
        keys_layout.setContentsMargins(20, 15, 20, 20)
        keys_layout.setSpacing(15)

        keys_label = QLabel("API Keys")
        keys_label.setStyleSheet("color: #ffffff; font-weight: bold; font-size: 14px;")
        keys_layout.addWidget(keys_label)

        # Anthropic API Key
        self._anthropic_key = self._create_key_input(
            "Anthropic API Key:",
            "Get from console.anthropic.com"
        )
        keys_layout.addWidget(self._anthropic_key["container"])

        # OpenAI API Key
        self._openai_key = self._create_key_input(
            "OpenAI API Key:",
            "Get from platform.openai.com"
        )
        keys_layout.addWidget(self._openai_key["container"])

        # Gemini API Key
        self._gemini_key = self._create_key_input(
            "Gemini API Key:",
            "Get from aistudio.google.com"
        )
        keys_layout.addWidget(self._gemini_key["container"])

        # Local endpoint
        local_container = QWidget()
        local_layout = QVBoxLayout(local_container)
        local_layout.setContentsMargins(0, 0, 0, 0)
        local_layout.setSpacing(4)

        local_label = QLabel("Local Model Endpoint:")
        local_label.setStyleSheet("color: #b0b0b0; font-size: 12px;")
        local_layout.addWidget(local_label)

        self._local_endpoint = QLineEdit()
        self._local_endpoint.setPlaceholderText("http://localhost:11434")
        self._style_input(self._local_endpoint)
        local_layout.addWidget(self._local_endpoint)

        local_hint = QLabel("For Ollama, LM Studio, or other local deployments")
        local_hint.setStyleSheet("color: #666666; font-size: 11px;")
        local_layout.addWidget(local_hint)

        keys_layout.addWidget(local_container)

        layout.addWidget(keys_frame)

        # Actions
        actions_frame = QFrame()
        actions_frame.setStyleSheet("background-color: #16213e;")
        actions_layout = QHBoxLayout(actions_frame)
        actions_layout.setContentsMargins(20, 10, 20, 20)
        actions_layout.setSpacing(10)

        self._test_btn = QPushButton("Test Connection")
        self._test_btn.setStyleSheet("""
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
        """)
        self._test_btn.clicked.connect(self._on_test_connection)
        actions_layout.addWidget(self._test_btn)

        actions_layout.addStretch()

        self._save_btn = QPushButton("Save Configuration")
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
        """)
        self._save_btn.clicked.connect(self._on_save)
        actions_layout.addWidget(self._save_btn)

        layout.addWidget(actions_frame)
        layout.addStretch()

    def _create_key_input(self, label_text: str, hint_text: str) -> dict:
        """Create a labeled API key input with show/hide toggle."""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        label = QLabel(label_text)
        label.setStyleSheet("color: #b0b0b0; font-size: 12px;")
        layout.addWidget(label)

        input_row = QHBoxLayout()
        input_row.setSpacing(8)

        key_input = QLineEdit()
        key_input.setEchoMode(QLineEdit.EchoMode.Password)
        key_input.setPlaceholderText("Enter API key")
        self._style_input(key_input)
        input_row.addWidget(key_input, stretch=1)

        show_btn = QPushButton("Show")
        show_btn.setCheckable(True)
        show_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a4a5a;
                color: #b0b0b0;
                border: none;
                border-radius: 4px;
                padding: 8px 12px;
            }
            QPushButton:hover {
                background-color: #4a5a6a;
            }
            QPushButton:checked {
                background-color: #4a9eff;
                color: white;
            }
        """)
        show_btn.clicked.connect(
            lambda checked: key_input.setEchoMode(
                QLineEdit.EchoMode.Normal if checked else QLineEdit.EchoMode.Password
            )
        )
        show_btn.clicked.connect(
            lambda checked: show_btn.setText("Hide" if checked else "Show")
        )
        input_row.addWidget(show_btn)

        layout.addLayout(input_row)

        hint = QLabel(hint_text)
        hint.setStyleSheet("color: #666666; font-size: 11px;")
        layout.addWidget(hint)

        return {"container": container, "input": key_input, "show_btn": show_btn}

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

    def set_config_service(self, service: ConfigService):
        """Set the config service and load current config."""
        self._config_service = service
        self._load_config()

    def _load_config(self):
        """Load current configuration into the form."""
        if not self._config_service:
            return

        config = self._config_service.get_config()

        # Set provider radio
        for btn in self._provider_group.buttons():
            if btn.property("provider_id") == config.llm.provider:
                btn.setChecked(True)
                break

        # Set API keys
        self._anthropic_key["input"].setText(config.llm.anthropic_api_key)
        self._openai_key["input"].setText(config.llm.openai_api_key)
        self._gemini_key["input"].setText(config.llm.gemini_api_key)
        self._local_endpoint.setText(config.llm.local_endpoint)

    def _get_selected_provider(self) -> str:
        """Get the selected provider ID."""
        checked = self._provider_group.checkedButton()
        if checked:
            return checked.property("provider_id")
        return "anthropic"

    def _on_test_connection(self):
        """Test the connection to the selected provider."""
        provider = self._get_selected_provider()

        # Get the appropriate key/endpoint
        if provider == "anthropic":
            key = self._anthropic_key["input"].text().strip()
            if not key:
                QMessageBox.warning(self, "Test Failed", "Please enter an Anthropic API key.")
                return
        elif provider == "openai":
            key = self._openai_key["input"].text().strip()
            if not key:
                QMessageBox.warning(self, "Test Failed", "Please enter an OpenAI API key.")
                return
        elif provider == "gemini":
            key = self._gemini_key["input"].text().strip()
            if not key:
                QMessageBox.warning(self, "Test Failed", "Please enter a Gemini API key.")
                return
        elif provider == "local":
            endpoint = self._local_endpoint.text().strip()
            if not endpoint:
                QMessageBox.warning(self, "Test Failed", "Please enter a local endpoint URL.")
                return

        # TODO: Implement actual connection test via API
        QMessageBox.information(
            self,
            "Test Connection",
            f"Connection test for {provider} would be performed here.\n"
            "This feature requires backend support."
        )

    def _on_save(self):
        """Save the configuration."""
        if not self._config_service:
            QMessageBox.warning(
                self,
                "Save Error",
                "Configuration service not available."
            )
            return

        try:
            config = self._config_service.get_config()

            # Update LLM config
            config.llm.provider = self._get_selected_provider()
            config.llm.anthropic_api_key = self._anthropic_key["input"].text().strip()
            config.llm.openai_api_key = self._openai_key["input"].text().strip()
            config.llm.gemini_api_key = self._gemini_key["input"].text().strip()
            config.llm.local_endpoint = self._local_endpoint.text().strip() or "http://localhost:11434"

            self._config_service.save(config)
            self.config_saved.emit()

            QMessageBox.information(
                self,
                "Saved",
                "LLM configuration saved successfully."
            )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Save Error",
                f"Failed to save configuration: {e}"
            )

    def get_config(self) -> LLMConfig:
        """Get the current form values as LLMConfig."""
        return LLMConfig(
            provider=self._get_selected_provider(),
            anthropic_api_key=self._anthropic_key["input"].text().strip(),
            openai_api_key=self._openai_key["input"].text().strip(),
            gemini_api_key=self._gemini_key["input"].text().strip(),
            local_endpoint=self._local_endpoint.text().strip() or "http://localhost:11434"
        )
