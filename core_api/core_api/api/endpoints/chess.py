"""Chess-specific API endpoints."""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from shared.chess_service import ChessGameService, PGNService, OpeningBook

router = APIRouter()

# Initialize services
opening_book = OpeningBook()


class MoveRequest(BaseModel):
    """Request to make a move."""
    fen: str
    move: str  # Can be SAN or UCI notation


class MoveResponse(BaseModel):
    """Response after making a move."""
    success: bool
    new_fen: str
    move_san: str
    move_uci: str
    is_check: bool
    is_checkmate: bool
    is_stalemate: bool
    game_over: bool
    result: Optional[str]


class PositionAnalysisRequest(BaseModel):
    """Request for position analysis."""
    fen: str


class PositionAnalysisResponse(BaseModel):
    """Response with position analysis."""
    fen: str
    legal_moves_san: List[str]
    legal_moves_uci: List[str]
    current_turn: str
    is_check: bool
    is_checkmate: bool
    is_stalemate: bool
    game_over: bool
    result: Optional[str]


class ValidateGameRequest(BaseModel):
    """Request to validate a game."""
    pgn: str


class ValidateGameResponse(BaseModel):
    """Response with game validation."""
    valid: bool
    error_message: Optional[str]
    move_count: int
    final_fen: str
    result: Optional[str]


@router.post("/move", response_model=MoveResponse)
def make_move(request: MoveRequest):
    """Make a move on the board."""
    try:
        game = ChessGameService()
        
        # Set the position
        if not game.set_board_fen(request.fen):
            raise HTTPException(status_code=400, detail="Invalid FEN position")
        
        # Try to make the move
        move_made = False
        if len(request.move) == 4 or len(request.move) == 5:  # Likely UCI
            move_made = game.make_move_from_uci(request.move)
        else:  # Likely SAN
            move_made = game.make_move_from_san(request.move)
        
        if not move_made:
            raise HTTPException(status_code=400, detail="Invalid or illegal move")
        
        # Get the move that was made
        last_move, san_move = game.move_history[-1]
        
        return MoveResponse(
            success=True,
            new_fen=game.get_board_fen(),
            move_san=san_move,
            move_uci=last_move.uci(),
            is_check=game.is_check(),
            is_checkmate=game.is_checkmate(),
            is_stalemate=game.is_stalemate(),
            game_over=game.is_game_over(),
            result=game.get_game_result()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing move: {str(e)}")


@router.post("/analyze", response_model=PositionAnalysisResponse)
def analyze_position(request: PositionAnalysisRequest):
    """Analyze a chess position."""
    try:
        game = ChessGameService()
        
        # Set the position
        if not game.set_board_fen(request.fen):
            raise HTTPException(status_code=400, detail="Invalid FEN position")
        
        return PositionAnalysisResponse(
            fen=request.fen,
            legal_moves_san=game.get_legal_moves_san(),
            legal_moves_uci=[move.uci() for move in game.get_legal_moves()],
            current_turn=game.get_current_turn(),
            is_check=game.is_check(),
            is_checkmate=game.is_checkmate(),
            is_stalemate=game.is_stalemate(),
            game_over=game.is_game_over(),
            result=game.get_game_result()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing position: {str(e)}")


@router.post("/validate", response_model=ValidateGameResponse)
def validate_game(request: ValidateGameRequest):
    """Validate a PGN game."""
    try:
        game = PGNService.import_game_from_pgn(request.pgn)
        
        if not game:
            return ValidateGameResponse(
                valid=False,
                error_message="Invalid PGN format or unable to parse game",
                move_count=0,
                final_fen="",
                result=None
            )
        
        return ValidateGameResponse(
            valid=True,
            error_message=None,
            move_count=len(game.move_history),
            final_fen=game.get_board_fen(),
            result=game.get_game_result()
        )
        
    except Exception as e:
        return ValidateGameResponse(
            valid=False,
            error_message=f"Error validating game: {str(e)}",
            move_count=0,
            final_fen="",
            result=None
        )


@router.get("/openings")
def list_openings():
    """Get list of available chess openings."""
    return {"openings": opening_book.get_all_openings()}


@router.get("/openings/{opening_name}")
def get_opening_info(opening_name: str):
    """Get information about a specific opening."""
    info = opening_book.get_opening_info(opening_name)
    if not info:
        raise HTTPException(status_code=404, detail="Opening not found")
    
    # Convert game service to moves list for JSON response
    moves_san = info["game_service"].get_move_history_san() if info["game_service"] else []
    
    return {
        "name": info["name"],
        "moves": info["moves"],
        "moves_san": moves_san,
        "final_fen": info["game_service"].get_board_fen() if info["game_service"] else None
    }


@router.get("/piece/{square}")
def get_piece_at_square(square: str, fen: str):
    """Get piece information at a specific square."""
    try:
        game = ChessGameService()
        
        if not game.set_board_fen(fen):
            raise HTTPException(status_code=400, detail="Invalid FEN position")
        
        piece_info = game.get_piece_at_square(square)
        return {"square": square, "piece": piece_info}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting piece info: {str(e)}")


@router.get("/starting-position")
def get_starting_position():
    """Get the starting chess position."""
    game = ChessGameService()
    return {
        "fen": game.get_board_fen(),
        "current_turn": game.get_current_turn(),
        "legal_moves_san": game.get_legal_moves_san()
    }