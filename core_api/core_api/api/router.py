"""API router configuration."""

from fastapi import APIRouter

from core_api.api.endpoints import auth, games, users, chess, analysis

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(games.router, prefix="/games", tags=["games"])
api_router.include_router(chess.router, prefix="/chess", tags=["chess"])
api_router.include_router(analysis.router, prefix="/analysis", tags=["analysis"])