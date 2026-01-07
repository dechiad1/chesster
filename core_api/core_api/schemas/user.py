"""User schemas."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    """Base user schema."""
    username: str
    email: EmailStr
    full_name: str
    nationality: Optional[str] = None
    avatar_path: Optional[str] = None
    rating: Optional[int] = None


class UserCreate(UserBase):
    """Schema for creating a user."""
    password: str


class UserUpdate(BaseModel):
    """Schema for updating a user."""
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    nationality: Optional[str] = None
    avatar_path: Optional[str] = None
    rating: Optional[int] = None
    is_active: Optional[bool] = None


class User(UserBase):
    """User schema with ID."""
    user_id: int
    registration_date: datetime
    last_login_date: Optional[datetime] = None
    is_active: bool
    
    class Config:
        from_attributes = True


class UserInDB(User):
    """User schema including password hash."""
    password_hash: str
    password_salt: str