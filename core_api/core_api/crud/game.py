"""Game CRUD operations."""

from typing import List, Optional
from sqlalchemy.orm import Session

from core_api.models.game import Game, GameNote, GameTag
from core_api.schemas.game import GameCreate, GameUpdate, GameNoteCreate, GameTagCreate


def get_game(db: Session, game_id: int) -> Optional[Game]:
    """Get a game by ID."""
    return db.query(Game).filter(Game.game_id == game_id).first()


def get_games(db: Session, skip: int = 0, limit: int = 100, user_id: Optional[int] = None) -> List[Game]:
    """Get games with optional filtering by user."""
    query = db.query(Game)
    
    if user_id is not None:
        query = query.filter(
            (Game.white_player_id == user_id) | (Game.black_player_id == user_id)
        )
    
    return query.offset(skip).limit(limit).all()


def create_game(db: Session, game: GameCreate) -> Game:
    """Create a new game."""
    db_game = Game(**game.dict())
    db.add(db_game)
    db.commit()
    db.refresh(db_game)
    return db_game


def update_game(db: Session, game_id: int, game_update: GameUpdate) -> Optional[Game]:
    """Update a game."""
    db_game = get_game(db, game_id)
    if not db_game:
        return None
    
    update_data = game_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_game, field, value)
    
    db.commit()
    db.refresh(db_game)
    return db_game


def delete_game(db: Session, game_id: int) -> bool:
    """Delete a game."""
    db_game = get_game(db, game_id)
    if not db_game:
        return False
    
    db.delete(db_game)
    db.commit()
    return True


def get_game_notes(db: Session, game_id: int) -> List[GameNote]:
    """Get notes for a game."""
    return db.query(GameNote).filter(GameNote.game_id == game_id).all()


def create_game_note(db: Session, note: GameNoteCreate) -> GameNote:
    """Create a new game note."""
    db_note = GameNote(**note.dict())
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note


def get_game_tags(db: Session, game_id: int) -> List[GameTag]:
    """Get tags for a game."""
    return db.query(GameTag).filter(GameTag.game_id == game_id).all()


def create_game_tag(db: Session, tag: GameTagCreate) -> GameTag:
    """Create a new game tag."""
    db_tag = GameTag(**tag.dict())
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag