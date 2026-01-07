"""Game API endpoints."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from core_api.crud import game as game_crud
from core_api.db.session import get_db
from core_api.schemas.game import Game, GameCreate, GameUpdate, GameNote, GameNoteCreate

router = APIRouter()


@router.get("/", response_model=List[Game])
def list_games(
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[int] = Query(None, description="Filter games by user ID"),
    db: Session = Depends(get_db)
):
    """List games with optional filtering."""
    games = game_crud.get_games(db, skip=skip, limit=limit, user_id=user_id)
    return games


@router.post("/", response_model=Game)
def create_game(game: GameCreate, db: Session = Depends(get_db)):
    """Create a new game."""
    return game_crud.create_game(db=db, game=game)


@router.get("/{game_id}", response_model=Game)
def get_game(game_id: int, db: Session = Depends(get_db)):
    """Get a specific game by ID."""
    db_game = game_crud.get_game(db, game_id=game_id)
    if db_game is None:
        raise HTTPException(status_code=404, detail="Game not found")
    return db_game


@router.put("/{game_id}", response_model=Game)
def update_game(game_id: int, game_update: GameUpdate, db: Session = Depends(get_db)):
    """Update a game."""
    db_game = game_crud.update_game(db, game_id=game_id, game_update=game_update)
    if db_game is None:
        raise HTTPException(status_code=404, detail="Game not found")
    return db_game


@router.delete("/{game_id}")
def delete_game(game_id: int, db: Session = Depends(get_db)):
    """Delete a game."""
    success = game_crud.delete_game(db, game_id=game_id)
    if not success:
        raise HTTPException(status_code=404, detail="Game not found")
    return {"message": "Game deleted successfully"}


@router.get("/{game_id}/notes", response_model=List[GameNote])
def get_game_notes(game_id: int, db: Session = Depends(get_db)):
    """Get notes for a game."""
    # Verify game exists
    db_game = game_crud.get_game(db, game_id=game_id)
    if db_game is None:
        raise HTTPException(status_code=404, detail="Game not found")
    
    return game_crud.get_game_notes(db, game_id=game_id)


@router.post("/{game_id}/notes", response_model=GameNote)
def create_game_note(game_id: int, note: GameNoteCreate, db: Session = Depends(get_db)):
    """Create a note for a game."""
    # Verify game exists
    db_game = game_crud.get_game(db, game_id=game_id)
    if db_game is None:
        raise HTTPException(status_code=404, detail="Game not found")
    
    # Override game_id from URL
    note.game_id = game_id
    return game_crud.create_game_note(db=db, note=note)


@router.get("/{game_id}/pgn")
def export_game_pgn(game_id: int, db: Session = Depends(get_db)):
    """Export game as PGN."""
    db_game = game_crud.get_game(db, game_id=game_id)
    if db_game is None:
        raise HTTPException(status_code=404, detail="Game not found")
    
    return {"pgn": db_game.pgn_data}


@router.post("/import")
def import_pgn(game: GameCreate, db: Session = Depends(get_db)):
    """Import a game from PGN data."""
    return game_crud.create_game(db=db, game=game)