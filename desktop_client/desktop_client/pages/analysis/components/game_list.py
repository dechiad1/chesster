"""Game list widget for the analysis page."""

import logging
from typing import Optional, List
from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QLineEdit, QComboBox, QFrame, QHeaderView
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont

from desktop_client.services.api_client import ChessAPIClient, APIError, GameData

logger = logging.getLogger(__name__)


class GameListWidget(QWidget):
    """Widget displaying list of games for analysis."""

    game_selected = pyqtSignal(int)  # game_id

    def __init__(self, parent=None):
        super().__init__(parent)
        self._api_client: Optional[ChessAPIClient] = None
        self._games: List[GameData] = []
        self._setup_ui()

    def _setup_ui(self):
        """Set up the game list UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header
        header = QFrame()
        header.setStyleSheet("background-color: #1a1a2e;")
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(15, 12, 15, 12)
        header_layout.setSpacing(8)

        title = QLabel("Your Games")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #ffffff;")
        header_layout.addWidget(title)

        # Filter row
        filter_row = QHBoxLayout()
        filter_row.setSpacing(10)

        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText("Search games...")
        self._search_input.setStyleSheet("""
            QLineEdit {
                background-color: #253156;
                color: #ffffff;
                border: 1px solid #3a4a6a;
                border-radius: 4px;
                padding: 6px 10px;
            }
            QLineEdit:focus {
                border-color: #4a9eff;
            }
        """)
        self._search_input.textChanged.connect(self._filter_games)
        filter_row.addWidget(self._search_input, stretch=1)

        self._source_filter = QComboBox()
        self._source_filter.addItems(["All Sources", "Desktop", "Chess.com", "Imported"])
        self._source_filter.setStyleSheet("""
            QComboBox {
                background-color: #253156;
                color: #ffffff;
                border: 1px solid #3a4a6a;
                border-radius: 4px;
                padding: 6px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #253156;
                color: #ffffff;
                selection-background-color: #4a9eff;
            }
        """)
        self._source_filter.currentTextChanged.connect(self._filter_games)
        filter_row.addWidget(self._source_filter)

        self._refresh_btn = QPushButton("Refresh")
        self._refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a9eff;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 16px;
            }
            QPushButton:hover {
                background-color: #3a8eef;
            }
        """)
        self._refresh_btn.clicked.connect(self.load_games)
        filter_row.addWidget(self._refresh_btn)

        header_layout.addLayout(filter_row)
        layout.addWidget(header)

        # Games table
        self._table = QTableWidget()
        self._table.setColumnCount(5)
        self._table.setHorizontalHeaderLabels(["Date", "Result", "Opening", "Source", "Moves"])
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setShowGrid(False)
        self._table.setAlternatingRowColors(True)
        self._table.verticalHeader().setVisible(False)

        # Style the table
        self._table.setStyleSheet("""
            QTableWidget {
                background-color: #16213e;
                color: #e0e0e0;
                border: none;
                gridline-color: #2a3a5a;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #2a3a5a;
            }
            QTableWidget::item:selected {
                background-color: #4a9eff;
            }
            QTableWidget::item:hover {
                background-color: #253156;
            }
            QHeaderView::section {
                background-color: #1a1a2e;
                color: #888888;
                padding: 10px;
                border: none;
                border-bottom: 2px solid #2a3a5a;
                font-weight: bold;
            }
        """)

        # Set column widths
        header_view = self._table.horizontalHeader()
        header_view.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header_view.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header_view.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header_view.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header_view.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)

        self._table.cellDoubleClicked.connect(self._on_game_double_clicked)
        layout.addWidget(self._table, stretch=1)

        # Footer
        footer = QFrame()
        footer.setStyleSheet("background-color: #1a1a2e;")
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(15, 10, 15, 10)

        self._count_label = QLabel("0 games")
        self._count_label.setStyleSheet("color: #888888; font-size: 12px;")
        footer_layout.addWidget(self._count_label)

        footer_layout.addStretch()

        layout.addWidget(footer)

    def set_api_client(self, client: ChessAPIClient):
        """Set the API client."""
        self._api_client = client

    def load_games(self):
        """Load games from the API."""
        if not self._api_client:
            return

        try:
            self._games = self._api_client.get_games(limit=100)
            self._populate_table(self._games)
        except APIError as e:
            logger.error(f"Failed to load games: {e}")

    def _populate_table(self, games: List[GameData]):
        """Populate the table with games."""
        self._table.setRowCount(len(games))

        for row, game in enumerate(games):
            # Date
            date_str = game.created_at[:10] if game.created_at else "Unknown"
            date_item = QTableWidgetItem(date_str)
            date_item.setData(Qt.ItemDataRole.UserRole, game.game_id)
            self._table.setItem(row, 0, date_item)

            # Result
            result = game.result or "In Progress"
            result_item = QTableWidgetItem(result)
            if result == "1-0":
                result_item.setForeground(Qt.GlobalColor.green)
            elif result == "0-1":
                result_item.setForeground(Qt.GlobalColor.red)
            self._table.setItem(row, 1, result_item)

            # Opening (extract from PGN if available)
            opening = self._extract_opening(game.pgn_data)
            self._table.setItem(row, 2, QTableWidgetItem(opening))

            # Source
            source = game.source or "Unknown"
            self._table.setItem(row, 3, QTableWidgetItem(source.title()))

            # Move count
            move_count = self._count_moves(game.pgn_data)
            self._table.setItem(row, 4, QTableWidgetItem(str(move_count)))

        self._count_label.setText(f"{len(games)} games")

    def _extract_opening(self, pgn_data: str) -> str:
        """Extract opening name from PGN data."""
        try:
            for line in pgn_data.split('\n'):
                if line.startswith('[Opening'):
                    return line.split('"')[1]
                if line.startswith('[ECO'):
                    return line.split('"')[1]
        except (IndexError, AttributeError):
            pass
        return "Unknown"

    def _count_moves(self, pgn_data: str) -> int:
        """Count moves in PGN data."""
        try:
            # Simple count: look for move numbers
            import re
            moves = re.findall(r'\d+\.', pgn_data)
            return len(moves)
        except Exception:
            return 0

    def _filter_games(self):
        """Filter displayed games based on search and source filter."""
        search_text = self._search_input.text().lower()
        source_filter = self._source_filter.currentText()

        filtered = []
        for game in self._games:
            # Source filter
            if source_filter != "All Sources":
                if source_filter.lower() != (game.source or "").lower():
                    continue

            # Search filter
            if search_text:
                opening = self._extract_opening(game.pgn_data).lower()
                if search_text not in opening and search_text not in (game.source or "").lower():
                    continue

            filtered.append(game)

        self._populate_table(filtered)

    def _on_game_double_clicked(self, row: int, column: int):
        """Handle game double-click."""
        item = self._table.item(row, 0)
        if item:
            game_id = item.data(Qt.ItemDataRole.UserRole)
            if game_id:
                self.game_selected.emit(game_id)

    def get_selected_game_id(self) -> Optional[int]:
        """Get the currently selected game ID."""
        selected = self._table.selectedItems()
        if selected:
            row = selected[0].row()
            item = self._table.item(row, 0)
            if item:
                return item.data(Qt.ItemDataRole.UserRole)
        return None
