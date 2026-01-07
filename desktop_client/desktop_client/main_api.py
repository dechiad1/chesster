"""Chess application with API integration."""

import sys
import logging
from typing import Optional
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QFileDialog, 
                            QListWidget, QTextEdit, QSplitter, QMessageBox,
                            QStatusBar, QListWidgetItem)
from PyQt6.QtCore import Qt, QRect, QTimer
from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QIcon, QShortcut, QKeySequence

from shared.chess_service import ChessGameService, PGNService, OpeningBook
from desktop_client.services.api_client import ChessAPIClient, APIError, GameData

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChessBoard(QWidget):
    """Chess board widget with API integration."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.game_service = ChessGameService()
        self.api_client: Optional[ChessAPIClient] = None
        self.current_game_id: Optional[int] = None
        
        # Visual settings
        self.selected_square = None
        self.square_size = 50
        self.light_square_color = QColor('#D2B48C')  
        self.dark_square_color = QColor('#769656')  
        self.selected_square_color = QColor(255, 255, 0, 127)
        self.piece_symbols = {
            'P': '♟', 'N': '♞', 'B': '♝', 'R': '♜', 'Q': '♛', 'K': '♚',
            'p': '♟', 'n': '♞', 'b': '♝', 'r': '♜', 'q': '♛', 'k': '♚',
        }
        self.setMinimumSize(self.square_size * 8, self.square_size * 8)
    
    def set_api_client(self, api_client: ChessAPIClient):
        """Set the API client for this board."""
        self.api_client = api_client
    
    def paintEvent(self, event):
        """Paint the chess board."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw squares
        for rank in range(8):
            for file in range(8):
                color = self.light_square_color if (rank + file) % 2 == 0 else self.dark_square_color
                square = QRect(file * self.square_size, (7-rank) * self.square_size, 
                             self.square_size, self.square_size)
                painter.fillRect(square, color)
                
                # Highlight selected square
                if self.selected_square is not None:
                    selected_file = self.selected_square % 8
                    selected_rank = self.selected_square // 8
                    if file == selected_file and rank == selected_rank:
                        painter.fillRect(square, self.selected_square_color)
        
        # Draw pieces using the game service
        font = QFont()
        font.setPointSize(24)
        painter.setFont(font)
        
        for rank in range(8):
            for file in range(8):
                square_name = chr(97 + file) + str(rank + 1)  # e.g., 'e4'
                piece_info = self.game_service.get_piece_at_square(square_name)
                
                if piece_info:
                    symbol = piece_info['unicode_symbol']
                    color = Qt.GlobalColor.white if piece_info['color'] == 'white' else Qt.GlobalColor.black
                    painter.setPen(QPen(color))
                    rect = QRect(file * self.square_size, (7-rank) * self.square_size,
                               self.square_size, self.square_size)
                    painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, symbol)
        
        # Draw coordinates
        font.setPointSize(10)
        painter.setFont(font)
        painter.setPen(QPen(Qt.GlobalColor.black))
        
        for i in range(8):
            rect = QRect(-20, i * self.square_size, 20, self.square_size)
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, str(8 - i))
            rect = QRect(i * self.square_size, 8 * self.square_size, self.square_size, 20)
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, chr(97 + i))
    
    def mousePressEvent(self, event):
        """Handle mouse clicks on the board."""
        file = int(event.position().x() // self.square_size)
        rank = int(event.position().y() // self.square_size)
        rank = 7 - rank  # Flip rank for proper coordinates
        
        if 0 <= file < 8 and 0 <= rank < 8:
            square = rank * 8 + file
            square_name = chr(97 + file) + str(rank + 1)
            
            if self.selected_square is None:
                # Select a square if it has a piece
                piece_info = self.game_service.get_piece_at_square(square_name)
                if piece_info and piece_info['color'] == self.game_service.get_current_turn():
                    self.selected_square = square
                    self.update()
            else:
                # Try to make a move
                from_square = chr(97 + (self.selected_square % 8)) + str((self.selected_square // 8) + 1)
                to_square = square_name
                move_uci = from_square + to_square
                
                if self.make_move(move_uci):
                    self.update()
                
                self.selected_square = None
                self.update()
    
    def make_move(self, move: str) -> bool:
        """Make a move using the game service."""
        try:
            # Try to make the move locally first
            success = self.game_service.make_move_from_uci(move) or self.game_service.make_move_from_san(move)
            
            if success:
                # If we have an API client and current game, save the move
                if self.api_client and self.current_game_id:
                    try:
                        self.save_current_game()
                    except APIError as e:
                        logger.warning(f"Failed to save move to API: {e}")
                        # Continue anyway - move was made locally
                
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error making move: {e}")
            return False
    
    def save_current_game(self):
        """Save the current game state to the API."""
        if not self.api_client or not self.current_game_id:
            return
        
        try:
            # Export current game as PGN
            pgn_data = PGNService.export_game_to_pgn(
                self.game_service,
                event="Desktop Game",
                site="Local",
                white="Player",
                black="Opponent"
            )
            
            # Update the game in the API
            self.api_client.update_game(
                self.current_game_id,
                pgn_data=pgn_data,
                result=self.game_service.get_game_result()
            )
            
        except APIError as e:
            logger.error(f"Failed to save game: {e}")
    
    def load_game_from_api(self, game_data: GameData):
        """Load a game from API data."""
        try:
            # Import the PGN data
            loaded_service = PGNService.import_game_from_pgn(game_data.pgn_data)
            if loaded_service:
                self.game_service = loaded_service
                self.current_game_id = game_data.game_id
                self.selected_square = None
                self.update()
                return True
        except Exception as e:
            logger.error(f"Failed to load game: {e}")
        
        return False
    
    def new_game(self):
        """Start a new game."""
        self.game_service.reset_game()
        self.current_game_id = None
        self.selected_square = None
        self.update()
    
    def goto_move(self, index: int):
        """Go to a specific move in the game."""
        self.game_service.goto_move(index)
        self.selected_square = None
        self.update()


class ChessApp(QMainWindow):
    """Main chess application with API integration."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chess Analysis Tool - API Version")
        self.api_client = ChessAPIClient()
        self.opening_book = OpeningBook()
        
        # Status tracking
        self.api_connected = False
        self.current_user_id = None
        
        self.setup_ui()
        self.check_api_connection()
    
    def setup_ui(self):
        """Set up the user interface."""
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)
        
        # Left panel - chess board
        board_container = QWidget()
        board_layout = QVBoxLayout(board_container)
        self.board_widget = ChessBoard()
        self.board_widget.set_api_client(self.api_client)
        board_layout.addWidget(self.board_widget)
        
        # Board controls
        controls = QHBoxLayout()
        self.new_game_btn = QPushButton("New Game")
        self.new_game_btn.clicked.connect(self.new_game)
        self.undo_btn = QPushButton("Undo Move")
        self.undo_btn.clicked.connect(self.undo_move)
        self.save_btn = QPushButton("Save Game")
        self.save_btn.clicked.connect(self.save_game)
        
        controls.addWidget(self.new_game_btn)
        controls.addWidget(self.undo_btn)
        controls.addWidget(self.save_btn)
        board_layout.addLayout(controls)
        
        layout.addWidget(board_container)
        
        # Right panel
        right_panel = QSplitter(Qt.Orientation.Vertical)
        
        # Top part - Game management and move list
        top_widget = QWidget()
        top_layout = QVBoxLayout(top_widget)
        
        # Game management controls
        game_controls = QHBoxLayout()
        self.load_games_btn = QPushButton("Load Games")
        self.load_games_btn.clicked.connect(self.load_games_list)
        self.load_pgn_btn = QPushButton("Load PGN File")
        self.load_pgn_btn.clicked.connect(self.load_pgn_file)
        self.save_pgn_btn = QPushButton("Save PGN")
        self.save_pgn_btn.clicked.connect(self.save_pgn_file)
        
        game_controls.addWidget(self.load_games_btn)
        game_controls.addWidget(self.load_pgn_btn)
        game_controls.addWidget(self.save_pgn_btn)
        top_layout.addLayout(game_controls)
        
        # Games list
        top_layout.addWidget(QLabel("Saved Games:"))
        self.games_list = QListWidget()
        self.games_list.itemDoubleClicked.connect(self.load_selected_game)
        top_layout.addWidget(self.games_list)
        
        # Move history
        top_layout.addWidget(QLabel("Move History:"))
        self.move_list = QListWidget()
        self.move_list.itemClicked.connect(self.move_selected)
        top_layout.addWidget(self.move_list)
        
        right_panel.addWidget(top_widget)
        
        # Bottom part - Openings and analysis
        bottom_widget = QWidget()
        bottom_layout = QVBoxLayout(bottom_widget)
        
        # Openings
        bottom_layout.addWidget(QLabel("Opening Book:"))
        self.openings_list = QListWidget()
        self.openings_list.addItems(self.opening_book.get_all_openings().keys())
        self.openings_list.itemClicked.connect(self.load_opening)
        bottom_layout.addWidget(self.openings_list)
        
        # Analysis
        bottom_layout.addWidget(QLabel("Analysis:"))
        self.analysis_text = QTextEdit()
        self.analysis_text.setReadOnly(True)
        bottom_layout.addWidget(self.analysis_text)
        
        right_panel.addWidget(bottom_widget)
        layout.addWidget(right_panel)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.update_status()
        
        # Auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.update_move_list)
        self.refresh_timer.start(1000)  # Update every second
    
    def check_api_connection(self):
        """Check API connection status."""
        try:
            self.api_connected = self.api_client.health_check()
            self.update_status()
            
            if not self.api_connected:
                QMessageBox.warning(
                    self, 
                    "API Connection", 
                    "Could not connect to the API server.\n"
                    "Make sure the server is running at http://localhost:8000\n"
                    "You can still use the app locally."
                )
        except Exception as e:
            logger.error(f"API connection check failed: {e}")
            self.api_connected = False
            self.update_status()
    
    def update_status(self):
        """Update the status bar."""
        api_status = "✅ API Connected" if self.api_connected else "❌ API Disconnected"
        turn = self.board_widget.game_service.get_current_turn().title()
        game_status = f"Turn: {turn}"
        
        if self.board_widget.game_service.is_game_over():
            result = self.board_widget.game_service.get_game_result()
            game_status = f"Game Over: {result}"
        
        self.status_bar.showMessage(f"{api_status} | {game_status}")
    
    def update_move_list(self):
        """Update the move history list."""
        self.move_list.clear()
        moves = self.board_widget.game_service.get_move_history_san()
        
        for i, move in enumerate(moves):
            move_number = i // 2 + 1
            if i % 2 == 0:
                self.move_list.addItem(f"{move_number}. {move}")
            else:
                prev_item = self.move_list.item(self.move_list.count() - 1)
                prev_item.setText(f"{prev_item.text()} {move}")
        
        # Highlight current move
        current_index = self.board_widget.game_service.current_move_index
        if current_index >= 0:
            item_index = current_index // 2
            if item_index < self.move_list.count():
                self.move_list.setCurrentRow(item_index)
        
        self.update_status()
    
    def new_game(self):
        """Start a new game."""
        self.board_widget.new_game()
        self.move_list.clear()
        self.analysis_text.clear()
        self.update_status()
    
    def undo_move(self):
        """Undo the last move."""
        if self.board_widget.game_service.undo_move():
            self.board_widget.update()
            self.update_move_list()
    
    def save_game(self):
        """Save the current game to the API."""
        if not self.api_connected:
            QMessageBox.warning(self, "Save Game", "API not connected. Cannot save game.")
            return
        
        try:
            # Export current game as PGN
            pgn_data = PGNService.export_game_to_pgn(
                self.board_widget.game_service,
                event="Desktop Game",
                site="Local",
                white="Player",
                black="Opponent"
            )
            
            # Create new game via API
            game_data = self.api_client.create_game(
                pgn_data=pgn_data,
                result=self.board_widget.game_service.get_game_result(),
                source="desktop"
            )
            
            self.board_widget.current_game_id = game_data.game_id
            QMessageBox.information(self, "Save Game", f"Game saved with ID: {game_data.game_id}")
            
            # Refresh games list
            self.load_games_list()
            
        except APIError as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save game: {e}")
    
    def load_games_list(self):
        """Load the list of saved games from the API."""
        if not self.api_connected:
            return
        
        try:
            games = self.api_client.get_games(limit=50)
            self.games_list.clear()
            
            for game in games:
                # Create a display name for the game
                result = game.result or "In Progress"
                created = game.created_at[:10] if game.created_at else "Unknown"
                display_name = f"Game {game.game_id} - {result} ({created})"
                
                item = QListWidgetItem(display_name)
                item.setData(Qt.ItemDataRole.UserRole, game.game_id)
                self.games_list.addItem(item)
                
        except APIError as e:
            QMessageBox.critical(self, "Load Error", f"Failed to load games: {e}")
    
    def load_selected_game(self, item: QListWidgetItem):
        """Load the selected game from the list."""
        try:
            game_id = item.data(Qt.ItemDataRole.UserRole)
            game_data = self.api_client.get_game(game_id)
            
            if self.board_widget.load_game_from_api(game_data):
                self.update_move_list()
                QMessageBox.information(self, "Load Game", f"Loaded game {game_id}")
            else:
                QMessageBox.warning(self, "Load Error", "Failed to load game data")
                
        except APIError as e:
            QMessageBox.critical(self, "Load Error", f"Failed to load game: {e}")
    
    def load_pgn_file(self):
        """Load a PGN file."""
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open PGN File", "", "PGN files (*.pgn);;All files (*)")
        
        if file_name:
            try:
                with open(file_name, 'r') as f:
                    pgn_content = f.read()
                
                # Try to load locally first
                loaded_service = PGNService.import_game_from_pgn(pgn_content)
                if loaded_service:
                    self.board_widget.game_service = loaded_service
                    self.board_widget.current_game_id = None  # Not saved yet
                    self.board_widget.update()
                    self.update_move_list()
                    
                    # If API is connected, offer to save
                    if self.api_connected:
                        reply = QMessageBox.question(
                            self, "Save Game", 
                            "Game loaded successfully. Save to API?",
                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                        )
                        if reply == QMessageBox.StandardButton.Yes:
                            self.save_game()
                else:
                    QMessageBox.warning(self, "Load Error", "Failed to parse PGN file")
                    
            except Exception as e:
                QMessageBox.critical(self, "Load Error", f"Error loading file: {e}")
    
    def save_pgn_file(self):
        """Save current game as PGN file."""
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Save PGN File", "", "PGN files (*.pgn);;All files (*)")
        
        if file_name:
            try:
                pgn_data = PGNService.export_game_to_pgn(
                    self.board_widget.game_service,
                    event="Desktop Game",
                    site="Local",
                    white="Player",
                    black="Opponent"
                )
                
                with open(file_name, 'w') as f:
                    f.write(pgn_data)
                
                QMessageBox.information(self, "Save Complete", f"Game saved to {file_name}")
                
            except Exception as e:
                QMessageBox.critical(self, "Save Error", f"Error saving file: {e}")
    
    def load_opening(self, item: QListWidgetItem):
        """Load a chess opening."""
        opening_name = item.text()
        if self.opening_book.load_opening_to_service(opening_name, self.board_widget.game_service):
            self.board_widget.current_game_id = None  # Reset game ID
            self.board_widget.update()
            self.update_move_list()
            self.analysis_text.setText(f"Loaded opening: {opening_name}")
    
    def move_selected(self, item: QListWidgetItem):
        """Handle move selection from the list."""
        move_index = self.move_list.row(item) * 2
        self.board_widget.goto_move(move_index)
    
    def closeEvent(self, event):
        """Handle application close."""
        if self.api_client:
            self.api_client.close()
        event.accept()


def main():
    """Main application entry point."""
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('./resources/chess-finesse.png'))
    
    window = ChessApp()
    window.resize(1200, 700)
    window.show()
    
    # Add keyboard shortcut for quitting
    quit_shortcut = QShortcut(QKeySequence("Ctrl+W"), window)
    quit_shortcut.activated.connect(window.close)
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()