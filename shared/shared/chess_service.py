"""Shared chess game service logic."""

from typing import List, Tuple, Optional, Dict, Any
import chess
import chess.pgn
import io
from datetime import datetime


class ChessGameService:
    """Service for managing chess game logic."""
    
    def __init__(self):
        self.board = chess.Board()
        self.move_history: List[Tuple[chess.Move, str]] = []
        self.current_move_index = -1
        
    def reset_game(self) -> None:
        """Reset the game to initial position."""
        self.board.reset()
        self.move_history = []
        self.current_move_index = -1
    
    def make_move(self, move: chess.Move) -> bool:
        """Make a move on the board if legal."""
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
    
    def make_move_from_san(self, san_move: str) -> bool:
        """Make a move using Standard Algebraic Notation."""
        try:
            move = self.board.parse_san(san_move)
            return self.make_move(move)
        except (ValueError, chess.IllegalMoveError, chess.InvalidMoveError):
            return False
    
    def make_move_from_uci(self, uci_move: str) -> bool:
        """Make a move using UCI notation (e.g., 'e2e4')."""
        try:
            move = chess.Move.from_uci(uci_move)
            return self.make_move(move)
        except (ValueError, chess.IllegalMoveError, chess.InvalidMoveError):
            return False
    
    def undo_move(self) -> bool:
        """Undo the last move."""
        if self.current_move_index >= 0:
            return self.goto_move(self.current_move_index - 1)
        return False
    
    def goto_move(self, index: int) -> bool:
        """Go to a specific move in the game history."""
        if 0 <= index < len(self.move_history):
            # Reset board and replay moves up to the selected index
            self.board.reset()
            for i in range(index + 1):
                self.board.push(self.move_history[i][0])
            self.current_move_index = index
            return True
        elif index == -1:
            # Go to initial position
            self.board.reset()
            self.current_move_index = -1
            return True
        return False
    
    def get_legal_moves(self) -> List[chess.Move]:
        """Get all legal moves for the current position."""
        return list(self.board.legal_moves)
    
    def get_legal_moves_san(self) -> List[str]:
        """Get all legal moves in SAN notation."""
        return [self.board.san(move) for move in self.board.legal_moves]
    
    def get_board_fen(self) -> str:
        """Get the current board position in FEN notation."""
        return self.board.fen()
    
    def set_board_fen(self, fen: str) -> bool:
        """Set the board position from FEN notation."""
        try:
            self.board.set_fen(fen)
            # Clear move history when setting a new position
            self.move_history = []
            self.current_move_index = -1
            return True
        except ValueError:
            return False
    
    def get_move_history_san(self) -> List[str]:
        """Get move history in SAN notation."""
        return [san_move for _, san_move in self.move_history]
    
    def get_move_history_uci(self) -> List[str]:
        """Get move history in UCI notation."""
        return [move.uci() for move, _ in self.move_history]
    
    def is_game_over(self) -> bool:
        """Check if the game is over."""
        return self.board.is_game_over()
    
    def get_game_result(self) -> Optional[str]:
        """Get the game result (1-0, 0-1, 1/2-1/2, or None if ongoing)."""
        if self.board.is_checkmate():
            return "1-0" if self.board.turn == chess.BLACK else "0-1"
        elif self.board.is_stalemate() or self.board.is_insufficient_material() or self.board.is_fifty_moves():
            return "1/2-1/2"
        elif self.board.is_repetition():
            return "1/2-1/2"
        return None
    
    def get_current_turn(self) -> str:
        """Get whose turn it is ('white' or 'black')."""
        return "white" if self.board.turn == chess.WHITE else "black"
    
    def is_check(self) -> bool:
        """Check if the current player is in check."""
        return self.board.is_check()
    
    def is_checkmate(self) -> bool:
        """Check if the current position is checkmate."""
        return self.board.is_checkmate()
    
    def is_stalemate(self) -> bool:
        """Check if the current position is stalemate."""
        return self.board.is_stalemate()
    
    def get_piece_at_square(self, square: str) -> Optional[Dict[str, Any]]:
        """Get piece information at a given square (e.g., 'e4')."""
        try:
            chess_square = chess.parse_square(square)
            piece = self.board.piece_at(chess_square)
            if piece:
                return {
                    "type": piece.piece_type,
                    "color": "white" if piece.color == chess.WHITE else "black",
                    "symbol": piece.symbol(),
                    "unicode_symbol": piece.unicode_symbol()
                }
            return None
        except ValueError:
            return None


class PGNService:
    """Service for handling PGN operations."""
    
    @staticmethod
    def export_game_to_pgn(
        game_service: ChessGameService,
        event: str = "Chess Game",
        site: str = "Local",
        date: Optional[str] = None,
        white: str = "White",
        black: str = "Black",
        result: Optional[str] = None,
        **headers
    ) -> str:
        """Export a game to PGN format."""
        game = chess.pgn.Game()
        
        # Set headers
        game.headers["Event"] = event
        game.headers["Site"] = site
        game.headers["Date"] = date or datetime.now().strftime("%Y.%m.%d")
        game.headers["White"] = white
        game.headers["Black"] = black
        game.headers["Result"] = result or game_service.get_game_result() or "*"
        
        # Add any additional headers
        for key, value in headers.items():
            game.headers[key] = value
        
        # Add moves
        node = game
        temp_board = chess.Board()
        for move, _ in game_service.move_history:
            node = node.add_variation(move)
            temp_board.push(move)
        
        return str(game)
    
    @staticmethod
    def import_game_from_pgn(pgn_text: str) -> Optional[ChessGameService]:
        """Import a game from PGN text."""
        try:
            pgn_io = io.StringIO(pgn_text)
            game = chess.pgn.read_game(pgn_io)
            
            if not game:
                return None
            
            service = ChessGameService()
            
            # Set starting position if specified
            if "FEN" in game.headers:
                service.set_board_fen(game.headers["FEN"])
            
            # Replay all moves
            for move in game.mainline_moves():
                service.make_move(move)
            
            return service
        except Exception:
            return None
    
    @staticmethod
    def get_pgn_headers(pgn_text: str) -> Dict[str, str]:
        """Extract headers from PGN text."""
        try:
            pgn_io = io.StringIO(pgn_text)
            game = chess.pgn.read_game(pgn_io)
            return dict(game.headers) if game else {}
        except Exception:
            return {}


class OpeningBook:
    """Service for chess opening recognition and information."""
    
    def __init__(self):
        self.openings = {
            "Sicilian Defense": "1. e4 c5",
            "French Defense": "1. e4 e6",
            "Caro-Kann Defense": "1. e4 c6",
            "Alekhine's Defense": "1. e4 Nf6",
            "Pirc Defense": "1. e4 d6",
            "Ruy Lopez": "1. e4 e5 2. Nf3 Nc6 3. Bb5",
            "Italian Game": "1. e4 e5 2. Nf3 Nc6 3. Bc4",
            "Scotch Game": "1. e4 e5 2. Nf3 Nc6 3. d4",
            "Four Knights Game": "1. e4 e5 2. Nf3 Nc6 3. Nc3 Nf6",
            "Queen's Gambit": "1. d4 d5 2. c4",
            "King's Indian Defense": "1. d4 Nf6 2. c4 g6",
            "Nimzo-Indian Defense": "1. d4 Nf6 2. c4 e6 3. Nc3 Bb4",
            "Queen's Indian Defense": "1. d4 Nf6 2. c4 e6 3. Nf3 b6",
            "English Opening": "1. c4",
            "Réti Opening": "1. Nf3"
        }
    
    def get_opening_info(self, opening_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific opening."""
        if opening_name in self.openings:
            return {
                "name": opening_name,
                "moves": self.openings[opening_name],
                "game_service": PGNService.import_game_from_pgn(self.openings[opening_name])
            }
        return None
    
    def get_all_openings(self) -> Dict[str, str]:
        """Get all available openings."""
        return self.openings.copy()
    
    def load_opening_to_service(self, opening_name: str, game_service: ChessGameService) -> bool:
        """Load an opening into a chess game service."""
        if opening_name in self.openings:
            temp_service = PGNService.import_game_from_pgn(self.openings[opening_name])
            if temp_service:
                game_service.reset_game()
                # Replay all moves from the opening
                for move, _ in temp_service.move_history:
                    game_service.make_move(move)
                return True
        return False