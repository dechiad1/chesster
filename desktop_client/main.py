import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QFileDialog, 
                            QListWidget, QTextEdit, QSplitter)
from PyQt6.QtCore import Qt, QRect
from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QIcon, QShortcut, QKeySequence
import chess
import chess.pgn
import io

class ChessBoard(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.board = chess.Board()
        self.selected_square = None
        self.square_size = 50
        self.light_square_color = QColor('#D2B48C')  
        self.dark_square_color = QColor('#769656')  
        self.selected_square_color = QColor(255, 255, 0, 127)
        self.piece_symbols = {
            'P': '♟', 'N': '♞', 'B': '♝', 'R': '♜', 'Q': '♛', 'K': '♚',
            'p': '♟', 'n': '♞', 'b': '♝', 'r': '♜', 'q': '♛', 'k': '♚',
        }
        self.move_history = []
        self.current_move_index = -1
        self.setMinimumSize(self.square_size * 8, self.square_size * 8)
    
    def paintEvent(self, event):
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
                    selected_file = chess.square_file(self.selected_square)
                    selected_rank = chess.square_rank(self.selected_square)
                    if file == selected_file and rank == selected_rank:
                        painter.fillRect(square, self.selected_square_color)
        
        # Draw pieces
        font = QFont()
        font.setPointSize(24)
        painter.setFont(font)
        
        for rank in range(8):
            for file in range(8):
                square = chess.square(file, rank)
                piece = self.board.piece_at(square)
                if piece:
                    symbol = self.piece_symbols[piece.symbol()]
                    color = Qt.GlobalColor.white if piece.color else Qt.GlobalColor.black
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
    
    def make_move(self, move):
        if move in self.board.legal_moves:
            san_move = self.board.san(move)
            self.board.push(move)
            # Truncate move history if we're not at the end
            if self.current_move_index < len(self.move_history) - 1:
                self.move_history = self.move_history[:self.current_move_index + 1]
            self.move_history.append((move, san_move))
            self.current_move_index += 1
            return True
        return False
    
    def mousePressEvent(self, event):
        file = event.position().x() // self.square_size
        rank = 7 - (event.position().y() // self.square_size)
        
        if 0 <= file < 8 and 0 <= rank < 8:
            square = chess.square(int(file), int(rank))
            
            if self.selected_square is None:
                if self.board.piece_at(square):
                    self.selected_square = square
                    self.update()
            else:
                move = chess.Move(self.selected_square, square)
                if self.make_move(move):
                    self.update()
                self.selected_square = None
                self.update()
    
    def goto_move(self, index):
        if 0 <= index < len(self.move_history):
            # Reset board
            self.board.reset()
            # Replay moves up to the selected index
            for i in range(index + 1):
                self.board.push(self.move_history[i][0])
            self.current_move_index = index
            self.selected_square = None
            self.update()

class ChessAnalyzer:
    def __init__(self):
        self.opening_book = {
            "Sicilian Defense": "1. e4 c5",
            "French Defense": "1. e4 e6",
            "Ruy Lopez": "1. e4 e5 2. Nf3 Nc6 3. Bb5",
            "Italian Game": "1. e4 e5 2. Nf3 Nc6 3. Bc4",
            "Queen's Gambit": "1. d4 d5 2. c4",
            "King's Indian Defense": "1. d4 Nf6 2. c4 g6"
        }
    
    def load_pgn(self, pgn_text):
        return chess.pgn.read_game(io.StringIO(pgn_text))

class ChessApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chess Analysis Tool")
        self.analyzer = ChessAnalyzer()
        self.setup_ui()
    
    def setup_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)
        
        # Left panel - chess board
        board_container = QWidget()
        board_layout = QVBoxLayout(board_container)
        self.board_widget = ChessBoard()
        board_layout.addWidget(self.board_widget)
        
        # Add control buttons under the board
        controls = QHBoxLayout()
        reset_btn = QPushButton("New Game")
        reset_btn.clicked.connect(self.reset_game)
        undo_btn = QPushButton("Undo Move")
        undo_btn.clicked.connect(self.undo_move)
        controls.addWidget(reset_btn)
        controls.addWidget(undo_btn)
        board_layout.addLayout(controls)
        
        layout.addWidget(board_container)
        
        # Right panel with splitter for move list and analysis
        right_panel = QSplitter(Qt.Orientation.Vertical)
        
        # Top part - Controls and move list
        top_widget = QWidget()
        top_layout = QVBoxLayout(top_widget)
        
        # PGN controls
        pgn_controls = QHBoxLayout()
        load_pgn_btn = QPushButton("Load PGN")
        load_pgn_btn.clicked.connect(self.load_pgn)
        save_pgn_btn = QPushButton("Save PGN")
        save_pgn_btn.clicked.connect(self.save_pgn)
        pgn_controls.addWidget(load_pgn_btn)
        pgn_controls.addWidget(save_pgn_btn)
        top_layout.addLayout(pgn_controls)
        
        # Move history
        top_layout.addWidget(QLabel("Move History:"))
        self.move_list = QListWidget()
        self.move_list.itemClicked.connect(self.move_selected)
        top_layout.addWidget(self.move_list)
        
        right_panel.addWidget(top_widget)
        
        # Bottom part - Opening book and analysis
        bottom_widget = QWidget()
        bottom_layout = QVBoxLayout(bottom_widget)
        
        # Openings list
        bottom_layout.addWidget(QLabel("Opening Book:"))
        self.openings_list = QListWidget()
        self.openings_list.addItems(self.analyzer.opening_book.keys())
        self.openings_list.itemClicked.connect(self.load_opening)
        bottom_layout.addWidget(self.openings_list)
        
        # Analysis text area
        bottom_layout.addWidget(QLabel("Analysis:"))
        self.analysis_text = QTextEdit()
        self.analysis_text.setReadOnly(True)
        bottom_layout.addWidget(self.analysis_text)
        
        right_panel.addWidget(bottom_widget)
        layout.addWidget(right_panel)
    
    def update_move_list(self):
        self.move_list.clear()
        for i, (_, san_move) in enumerate(self.board_widget.move_history):
            move_number = i // 2 + 1
            if i % 2 == 0:
                self.move_list.addItem(f"{move_number}. {san_move}")
            else:
                prev_text = self.move_list.item(self.move_list.count() - 1).text()
                self.move_list.item(self.move_list.count() - 1).setText(f"{prev_text} {san_move}")
        
        # Highlight current move
        if self.board_widget.current_move_index >= 0:
            current_item = self.move_list.item(self.board_widget.current_move_index // 2)
            self.move_list.setCurrentItem(current_item)
    
    def move_selected(self, item):
        move_text = item.text()
        move_index = self.move_list.row(item) * 2
        # If it's a full move (includes both white and black moves)
        if " " in move_text and move_text.split(" ")[1] != "...":
            # If we clicked the second move, increment the index
            if self.board_widget.current_move_index % 2 == 0:
                move_index += 1
        self.board_widget.goto_move(move_index)
        self.update_move_list()
    
    def reset_game(self):
        self.board_widget.board.reset()
        self.board_widget.move_history = []
        self.board_widget.current_move_index = -1
        self.board_widget.selected_square = None
        self.board_widget.update()
        self.move_list.clear()
        self.analysis_text.clear()
    
    def undo_move(self):
        if self.board_widget.current_move_index >= 0:
            self.board_widget.goto_move(self.board_widget.current_move_index - 1)
            self.update_move_list()
    
    def load_pgn(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open PGN File", "", "PGN files (*.pgn)")
        if file_name:
            with open(file_name) as f:
                game = self.analyzer.load_pgn(f.read())
                if game:
                    # Reset the board and move history
                    self.reset_game()
                    # Replay all moves from the PGN
                    board = game.board()
                    for move in game.mainline_moves():
                        self.board_widget.make_move(move)
                    self.update_move_list()
    
    def save_pgn(self):
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Save PGN File", "", "PGN files (*.pgn)")
        if file_name:
            game = chess.pgn.Game.from_board(self.board_widget.board)
            with open(file_name, 'w') as f:
                print(game, file=f)
    
    def load_opening(self, item):
        opening_moves = self.analyzer.opening_book[item.text()]
        game = self.analyzer.load_pgn(opening_moves)
        if game:
            self.reset_game()
            board = game.board()
            for move in game.mainline_moves():
                self.board_widget.make_move(move)
            self.update_move_list()
            self.analysis_text.setText(f"Loaded {item.text()}\n{opening_moves}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('./resources/chess-finesse.png'))

    # Enable Cmd+W (or Ctrl+W on Windows/Linux) to close the application
    app.aboutToQuit.connect(lambda: sys.exit(0))
    window = ChessApp()
    window.resize(1000, 600)
    window.show()

    # Add shortcut for Cmd+W (or Ctrl+W)
    quit_shortcut = QShortcut(QKeySequence("Ctrl+W"), window)
    quit_shortcut.activated.connect(window.close)

    sys.exit(app.exec())
    window = ChessApp()
    window.resize(1000, 600)
    window.show()
    sys.exit(app.exec())