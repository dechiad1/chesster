"""User model."""

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship

from core_api.db.base import Base


class User(Base):
    """User model."""
    
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    full_name = Column(String(100), nullable=False)
    nationality = Column(String(50), nullable=True)
    avatar_path = Column(String(255), nullable=True)
    rating = Column(Integer, nullable=True)
    registration_date = Column(DateTime, default=datetime.utcnow)
    last_login_date = Column(DateTime, nullable=True)
    password_hash = Column(String(255), nullable=False)
    password_salt = Column(String(50), nullable=False)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    white_games = relationship("Game", back_populates="white_player", foreign_keys="Game.white_player_id")
    black_games = relationship("Game", back_populates="black_player", foreign_keys="Game.black_player_id")
    notes = relationship("GameNote", back_populates="user")
    
    def __repr__(self) -> str:
        return f"<User(username='{self.username}', email='{self.email}')>"