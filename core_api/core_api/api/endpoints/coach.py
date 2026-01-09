"""Coach chat API endpoints."""

import logging
from typing import List, Optional, Literal

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


class ChessLine(BaseModel):
    """Represents a suggested chess variation/line."""
    description: str  # e.g., "Main attacking continuation"
    moves: List[str]  # UCI format: ["e2e4", "e7e5", "g1f3"]
    moves_san: List[str]  # SAN format for display: ["e4", "e5", "Nf3"]
    evaluation: Optional[float] = None  # Centipawns after the line


class ChatResponse(BaseModel):
    """Chat response model - can contain text or suggested lines."""
    response_type: Literal["text", "lines"] = "text"
    content: str  # Text content or intro for lines
    lines: Optional[List[ChessLine]] = None  # Suggested variations (if response_type == "lines")

    # For backward compatibility
    response: Optional[str] = None  # Deprecated, use content instead

    def __init__(self, **data):
        """Initialize with backward compatibility."""
        # If old 'response' field is used, copy to 'content'
        if 'response' in data and 'content' not in data:
            data['content'] = data['response']
        super().__init__(**data)


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
        response_dict = coach.chat(
            message=request.message,
            fen=request.fen,
            move_history=request.move_history
        )

        # Convert lines dicts to ChessLine models if present
        lines = None
        if response_dict.get("lines"):
            lines = [ChessLine(**line) for line in response_dict["lines"]]

        return ChatResponse(
            response_type=response_dict["response_type"],
            content=response_dict["content"],
            lines=lines,
            response=response_dict["content"]  # For backward compatibility
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Coach chat error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Chat failed: {str(e)}"
        )
