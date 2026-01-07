"""User CRUD operations."""

from typing import Optional
from sqlalchemy.orm import Session
from passlib.context import CryptContext
import secrets

from core_api.models.user import User
from core_api.schemas.user import UserCreate, UserUpdate

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> tuple[str, str]:
    """Hash a password with a random salt."""
    salt = secrets.token_hex(16)
    hashed = pwd_context.hash(password + salt)
    return hashed, salt


def verify_password(plain_password: str, salt: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password + salt, hashed_password)


def get_user(db: Session, user_id: int) -> Optional[User]:
    """Get a user by ID."""
    return db.query(User).filter(User.user_id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get a user by email."""
    return db.query(User).filter(User.email == email).first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Get a user by username."""
    return db.query(User).filter(User.username == username).first()


def create_user(db: Session, user: UserCreate) -> User:
    """Create a new user."""
    hashed_password, salt = get_password_hash(user.password)
    
    db_user = User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        nationality=user.nationality,
        avatar_path=user.avatar_path,
        rating=user.rating,
        password_hash=hashed_password,
        password_salt=salt
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: int, user_update: UserUpdate) -> Optional[User]:
    """Update a user."""
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    update_data = user_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user