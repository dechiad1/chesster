"""Game model."""

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship

from core_api.db.base import Base


class Game(Base):
    """Game model."""
    
    __tablename__ = "games"
    
    game_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    white_player_id = Column(Integer, ForeignKey("users.user_id"), nullable=True)
    black_player_id = Column(Integer, ForeignKey("users.user_id"), nullable=True)
    start_datetime = Column(DateTime, nullable=True)
    end_datetime = Column(DateTime, nullable=True)
    result = Column(String(10), nullable=True)  # "1-0", "0-1", "1/2-1/2", "*"
    pgn_data = Column(Text, nullable=False)
    source = Column(String(50), nullable=True)  # "local", "chess.com", "lichess", etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    white_player = relationship("User", back_populates="white_games", foreign_keys=[white_player_id])
    black_player = relationship("User", back_populates="black_games", foreign_keys=[black_player_id])
    notes = relationship("GameNote", back_populates="game")
    tags = relationship("GameTag", back_populates="game")
    
    def __repr__(self) -> str:
        return f"<Game(game_id={self.game_id}, result='{self.result}')>"


class GameNote(Base):
    """Game note model."""
    
    __tablename__ = "game_notes"
    
    note_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    game_id = Column(Integer, ForeignKey("games.game_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    note_text = Column(Text, nullable=True)
    annotation = Column(String(10), nullable=True)  # "?", "??", "!", "!!", "!?", "?!"
    is_game_level = Column(Integer, default=0)  # 0 = move level, 1 = game level
    move_number = Column(Integer, nullable=True)
    side = Column(String(1), nullable=True)  # "w" or "b"
    created_at = Column(DateTime, default=datetime.utcnow)
    modified_at = Column(DateTime, nullable=True)
    
    # Relationships
    game = relationship("Game", back_populates="notes")
    user = relationship("User", back_populates="notes")
    
    def __repr__(self) -> str:
        return f"<GameNote(note_id={self.note_id}, game_id={self.game_id})>"


class GameTag(Base):
    """Game tag model."""
    
    __tablename__ = "game_tags"
    
    tag_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    game_id = Column(Integer, ForeignKey("games.game_id"), nullable=False)
    tag_name = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    game = relationship("Game", back_populates="tags")
    
    def __repr__(self) -> str:
        return f"<GameTag(tag_name='{self.tag_name}', game_id={self.game_id})>"