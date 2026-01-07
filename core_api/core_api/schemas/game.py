"""Game schemas."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class GameBase(BaseModel):
    """Base game schema."""
    white_player_id: Optional[int] = None
    black_player_id: Optional[int] = None
    start_datetime: Optional[datetime] = None
    end_datetime: Optional[datetime] = None
    result: Optional[str] = None
    pgn_data: str
    source: Optional[str] = None


class GameCreate(GameBase):
    """Schema for creating a game."""
    pass


class GameUpdate(BaseModel):
    """Schema for updating a game."""
    white_player_id: Optional[int] = None
    black_player_id: Optional[int] = None
    start_datetime: Optional[datetime] = None
    end_datetime: Optional[datetime] = None
    result: Optional[str] = None
    pgn_data: Optional[str] = None
    source: Optional[str] = None


class Game(GameBase):
    """Game schema with ID."""
    game_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class GameNoteBase(BaseModel):
    """Base game note schema."""
    note_text: Optional[str] = None
    annotation: Optional[str] = None
    is_game_level: int = 0
    move_number: Optional[int] = None
    side: Optional[str] = None


class GameNoteCreate(GameNoteBase):
    """Schema for creating a game note."""
    game_id: int
    user_id: int


class GameNote(GameNoteBase):
    """Game note schema with ID."""
    note_id: int
    game_id: int
    user_id: int
    created_at: datetime
    modified_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class GameTagBase(BaseModel):
    """Base game tag schema."""
    tag_name: str


class GameTagCreate(GameTagBase):
    """Schema for creating a game tag."""
    game_id: int


class GameTag(GameTagBase):
    """Game tag schema with ID."""
    tag_id: int
    game_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True