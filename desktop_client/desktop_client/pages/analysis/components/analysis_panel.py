"""Analysis panel widget for displaying LLM game analysis."""

import logging
from typing import Optional

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTextEdit, QFrame, QProgressBar
)
from PyQt6.QtCore import pyqtSignal, QThread, pyqtSlot
from PyQt6.QtGui import QFont

from desktop_client.services.api_client import ChessAPIClient, APIError

logger = logging.getLogger(__name__)


class AnalysisWorker(QThread):
    """Worker thread for running game analysis."""

    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(
        self,
        api_client: ChessAPIClient,
        game_id: int,
        pgn_data: str,
        provider: str,
        api_key: str
    ):
        super().__init__()
        self.api_client = api_client
        self.game_id = game_id
        self.pgn_data = pgn_data
        self.provider = provider
        self.api_key = api_key

    def run(self):
        """Run the analysis."""
        try:
            result = self.api_client.analyze_game(
                game_id=self.game_id,
                pgn_data=self.pgn_data,
                provider=self.provider,
                api_key=self.api_key
            )
            self.finished.emit(result)
        except APIError as e:
            self.error.emit(str(e))
        except Exception as e:
            self.error.emit(f"Analysis failed: {e}")


class AnalysisPanelWidget(QWidget):
    """Panel for displaying game analysis results."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._api_client: Optional[ChessAPIClient] = None
        self._provider: str = "anthropic"
        self._api_key: str = ""
        self._current_game_id: Optional[int] = None
        self._current_pgn: Optional[str] = None
        self._worker: Optional[AnalysisWorker] = None
        self._setup_ui()

    def _setup_ui(self):
        """Set up the panel UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header
        header = QFrame()
        header.setStyleSheet("background-color: #1a1a2e;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(15, 12, 15, 12)

        title = QLabel("Game Analysis")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #ffffff;")
        header_layout.addWidget(title)

        header_layout.addStretch()

        self._analyze_btn = QPushButton("Analyze Game")
        self._analyze_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a9eff;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3a8eef;
            }
            QPushButton:disabled {
                background-color: #3a4a5a;
                color: #888888;
            }
        """)
        self._analyze_btn.clicked.connect(self._on_analyze)
        self._analyze_btn.setEnabled(False)
        header_layout.addWidget(self._analyze_btn)

        layout.addWidget(header)

        # Progress bar
        self._progress = QProgressBar()
        self._progress.setRange(0, 0)  # Indeterminate
        self._progress.setStyleSheet("""
            QProgressBar {
                background-color: #16213e;
                border: none;
                height: 4px;
            }
            QProgressBar::chunk {
                background-color: #4a9eff;
            }
        """)
        self._progress.setVisible(False)
        layout.addWidget(self._progress)

        # Content area
        content = QFrame()
        content.setStyleSheet("background-color: #16213e;")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(15, 15, 15, 15)
        content_layout.setSpacing(10)

        # Status/instructions
        self._status_label = QLabel("Select a game to analyze")
        self._status_label.setStyleSheet("color: #888888; font-size: 13px;")
        content_layout.addWidget(self._status_label)

        # Analysis results
        self._results_text = QTextEdit()
        self._results_text.setReadOnly(True)
        self._results_text.setStyleSheet("""
            QTextEdit {
                background-color: #253156;
                color: #e0e0e0;
                border: 1px solid #3a4a6a;
                border-radius: 6px;
                padding: 12px;
                font-size: 13px;
                line-height: 1.5;
            }
        """)
        self._results_text.setPlaceholderText(
            "Analysis results will appear here after you click 'Analyze Game'.\n\n"
            "The AI will review the game and identify:\n"
            "• Critical moments and turning points\n"
            "• Mistakes and blunders\n"
            "• Missed opportunities\n"
            "• Recommendations for improvement"
        )
        content_layout.addWidget(self._results_text, stretch=1)

        layout.addWidget(content, stretch=1)

    def set_api_client(self, client: ChessAPIClient):
        """Set the API client."""
        self._api_client = client

    def set_llm_config(self, provider: str, api_key: str):
        """Set the LLM configuration."""
        self._provider = provider
        self._api_key = api_key

    def set_game(self, game_id: int, pgn_data: str):
        """Set the current game for analysis.

        Args:
            game_id: Game ID
            pgn_data: PGN data of the game
        """
        self._current_game_id = game_id
        self._current_pgn = pgn_data
        self._analyze_btn.setEnabled(True)
        self._status_label.setText(f"Ready to analyze game #{game_id}")
        self._results_text.clear()

    def _on_analyze(self):
        """Start game analysis."""
        if not self._api_client:
            self._show_error("API not connected")
            return

        if not self._api_key:
            self._show_error("Please configure your LLM API key in Settings")
            return

        if not self._current_pgn:
            self._show_error("No game selected")
            return

        self._set_loading(True)
        self._status_label.setText("Analyzing game...")

        self._worker = AnalysisWorker(
            self._api_client,
            self._current_game_id or 0,
            self._current_pgn,
            self._provider,
            self._api_key
        )
        self._worker.finished.connect(self._on_analysis_complete)
        self._worker.error.connect(self._on_analysis_error)
        self._worker.start()

    def _set_loading(self, loading: bool):
        """Set loading state."""
        self._analyze_btn.setEnabled(not loading)
        self._progress.setVisible(loading)

    @pyqtSlot(dict)
    def _on_analysis_complete(self, result: dict):
        """Handle analysis completion."""
        self._set_loading(False)
        self._status_label.setText("Analysis complete")

        # Format the results
        self._format_analysis(result)

    def _format_analysis(self, result: dict):
        """Format and display analysis results."""
        text = ""

        # Summary
        if "summary" in result:
            text += f"📋 SUMMARY\n{'=' * 40}\n{result['summary']}\n\n"

        # Critical moments
        if "critical_moments" in result:
            text += f"⚡ CRITICAL MOMENTS\n{'=' * 40}\n"
            for moment in result["critical_moments"]:
                text += f"• Move {moment.get('move_number', '?')}: {moment.get('description', '')}\n"
                if moment.get('evaluation'):
                    text += f"  Evaluation: {moment['evaluation']}\n"
            text += "\n"

        # Mistakes
        if "mistakes" in result:
            text += f"❌ MISTAKES\n{'=' * 40}\n"
            for mistake in result["mistakes"]:
                text += f"• Move {mistake.get('move_number', '?')}: {mistake.get('move', '')}\n"
                text += f"  {mistake.get('explanation', '')}\n"
                if mistake.get('better_move'):
                    text += f"  Better: {mistake['better_move']}\n"
            text += "\n"

        # Blunders
        if "blunders" in result:
            text += f"💥 BLUNDERS\n{'=' * 40}\n"
            for blunder in result["blunders"]:
                text += f"• Move {blunder.get('move_number', '?')}: {blunder.get('move', '')}\n"
                text += f"  {blunder.get('explanation', '')}\n"
                if blunder.get('better_move'):
                    text += f"  Better: {blunder['better_move']}\n"
            text += "\n"

        # Recommendations
        if "recommendations" in result:
            text += f"💡 RECOMMENDATIONS\n{'=' * 40}\n"
            for i, rec in enumerate(result["recommendations"], 1):
                text += f"{i}. {rec}\n"
            text += "\n"

        # If no structured data, show raw
        if not text:
            if "analysis" in result:
                text = result["analysis"]
            elif "response" in result:
                text = result["response"]
            else:
                text = str(result)

        self._results_text.setPlainText(text)

    @pyqtSlot(str)
    def _on_analysis_error(self, error: str):
        """Handle analysis error."""
        self._set_loading(False)
        self._show_error(error)

    def _show_error(self, message: str):
        """Display an error message."""
        self._status_label.setText(f"Error: {message}")
        self._status_label.setStyleSheet("color: #dc3545; font-size: 13px;")

    def clear(self):
        """Clear the panel."""
        self._current_game_id = None
        self._current_pgn = None
        self._analyze_btn.setEnabled(False)
        self._status_label.setText("Select a game to analyze")
        self._status_label.setStyleSheet("color: #888888; font-size: 13px;")
        self._results_text.clear()
