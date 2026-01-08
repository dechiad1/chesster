"""Coach chat API endpoints."""

import logging
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from core_api.adapters.llm.factory import create_llm_provider
from core_api.adapters.chess_engine.stockfish_adapter import StockfishAdapter
from core_api.services.coach_service import CoachService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/coach", tags=["coach"])


class ChatRequest(BaseModel):
    """Chat request model."""
    message: str
    fen: str
    move_history: List[str]
    provider: str = "anthropic"
    api_key: str


class ChatResponse(BaseModel):
    """Chat response model."""
    response: str


@router.post("/chat", response_model=ChatResponse)
async def coach_chat(request: ChatRequest):
    """Chat with the chess coach.

    The coach will answer questions about the current position,
    strategy, tactics, and chess concepts. It has access to
    Stockfish for position evaluation.

    Args:
        request: Chat request with message and game context

    Returns:
        Coach's response
    """
    if not request.api_key:
        raise HTTPException(
            status_code=400,
            detail="API key is required"
        )

    # Create LLM provider
    llm_provider = create_llm_provider(
        provider=request.provider,
        api_key=request.api_key
    )

    if not llm_provider:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid LLM provider: {request.provider}"
        )

    # Try to create chess engine (optional)
    chess_engine = None
    try:
        engine = StockfishAdapter()
        if engine.is_available():
            chess_engine = engine
    except Exception as e:
        logger.warning(f"Stockfish not available: {e}")

    # Create coach service
    coach = CoachService(llm_provider, chess_engine)

    try:
        response = coach.chat(
            message=request.message,
            fen=request.fen,
            move_history=request.move_history
        )
        return ChatResponse(response=response)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Coach chat error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Chat failed: {str(e)}"
        )
