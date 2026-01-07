"""Authentication API endpoints."""

from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.post("/register")
def register():
    """Register a new user (placeholder)."""
    raise HTTPException(status_code=501, detail="Authentication not implemented yet")


@router.post("/login")
def login():
    """User login (placeholder)."""
    raise HTTPException(status_code=501, detail="Authentication not implemented yet")


@router.post("/logout")
def logout():
    """User logout (placeholder)."""
    raise HTTPException(status_code=501, detail="Authentication not implemented yet")