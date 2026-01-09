"""API endpoints for chess.com integration and LLM analysis."""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import logging

from core_api.schemas.analysis import (
    FetchGamesRequest,
    FetchGamesResponse,
    AnalyzeGamesRequest,
    AnalyzeGamesResponse,
    ChessComGameSchema,
    ChessComProfileSchema,
    GameTrendAnalysisSchema
)
from core_api.services.chesscom_service import (
    ChessComService,
    ChessComServiceError
)
from core_api.services.llm_analysis_service import (
    LLMAnalysisService,
    LLMAnalysisError
)
from core_api.adapters.llm.factory import create_llm_provider
from core_api.adapters.chess_engine.stockfish_adapter import StockfishAdapter
from core_api.services.move_analysis_service import MoveAnalysisService

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/chesscom/profile/{username}", response_model=ChessComProfileSchema)
async def get_chesscom_profile(username: str):
    """Get a player's Chess.com profile.

    Args:
        username: Chess.com username

    Returns:
        Player profile information
    """
    try:
        with ChessComService() as service:
            profile = service.get_player_profile(username)
            return ChessComProfileSchema(
                username=profile.username,
                player_id=profile.player_id,
                url=profile.url,
                country=profile.country,
                joined=profile.joined,
                last_online=profile.last_online,
                followers=profile.followers,
                is_streamer=profile.is_streamer
            )
    except ChessComServiceError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error fetching profile: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch profile")


@router.post("/chesscom/games", response_model=FetchGamesResponse)
async def fetch_chesscom_games(request: FetchGamesRequest):
    """Fetch recent games from Chess.com for a player.

    Args:
        request: Contains username and count of games to fetch

    Returns:
        List of recent games
    """
    try:
        with ChessComService() as service:
            games = service.get_recent_games(request.username, request.count)

            game_schemas = [
                ChessComGameSchema(
                    url=game.url,
                    pgn=game.pgn,
                    time_control=game.time_control,
                    end_time=game.end_time,
                    rated=game.rated,
                    time_class=game.time_class,
                    rules=game.rules,
                    white_username=game.white_username,
                    white_rating=game.white_rating,
                    white_result=game.white_result,
                    black_username=game.black_username,
                    black_rating=game.black_rating,
                    black_result=game.black_result,
                    opening=game.opening
                )
                for game in games
            ]

            return FetchGamesResponse(
                username=request.username,
                games_count=len(game_schemas),
                games=game_schemas
            )
    except ChessComServiceError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error fetching games: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch games")


@router.post("/analyze", response_model=AnalyzeGamesResponse)
async def analyze_games(request: AnalyzeGamesRequest):
    """Analyze a player's recent games using LLM.

    This endpoint fetches the player's recent games from Chess.com
    and uses an LLM (Claude) to analyze trends and provide recommendations.

    Args:
        request: Contains username, API key, and game count

    Returns:
        Analysis results with insights and recommendations
    """
    try:
        # First, fetch the games from Chess.com
        with ChessComService() as chesscom_service:
            games = chesscom_service.get_recent_games(request.username, request.count)

        if not games:
            return AnalyzeGamesResponse(
                success=False,
                error=f"No games found for user '{request.username}'"
            )

        # Analyze the games with LLM
        with LLMAnalysisService(request.api_key) as llm_service:
            analysis = llm_service.analyze_games(games, request.username)

            return AnalyzeGamesResponse(
                success=True,
                analysis=GameTrendAnalysisSchema(
                    username=analysis.username,
                    games_analyzed=analysis.games_analyzed,
                    analysis_date=analysis.analysis_date,
                    summary=analysis.summary,
                    strengths=analysis.strengths,
                    weaknesses=analysis.weaknesses,
                    opening_trends=analysis.opening_trends,
                    time_management=analysis.time_management,
                    recommendations=analysis.recommendations,
                    win_rate=analysis.win_rate,
                    most_played_openings=analysis.most_played_openings
                )
            )

    except ChessComServiceError as e:
        return AnalyzeGamesResponse(
            success=False,
            error=f"Chess.com error: {str(e)}"
        )
    except LLMAnalysisError as e:
        return AnalyzeGamesResponse(
            success=False,
            error=f"Analysis error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error during analysis: {e}")
        return AnalyzeGamesResponse(
            success=False,
            error="An unexpected error occurred during analysis"
        )


class GameAnalysisRequest(BaseModel):
    """Request model for single game analysis."""
    game_id: int
    pgn_data: str
    provider: str = "anthropic"
    api_key: str


class GameAnalysisResponse(BaseModel):
    """Response model for game analysis."""
    success: bool = True
    summary: Optional[str] = None
    critical_moments: Optional[List[Dict[str, Any]]] = None
    mistakes: Optional[List[Dict[str, Any]]] = None
    blunders: Optional[List[Dict[str, Any]]] = None
    recommendations: Optional[List[str]] = None
    error: Optional[str] = None


@router.post("/game", response_model=GameAnalysisResponse)
async def analyze_single_game(request: GameAnalysisRequest):
    """Analyze a single game for mistakes and blunders.

    Uses the LLM to analyze the game PGN and identify:
    - Critical moments and turning points
    - Mistakes and blunders
    - Recommendations for improvement

    If Stockfish is available, it will be used to identify
    objective mistakes before sending to the LLM.

    Args:
        request: Game analysis request with PGN and provider info

    Returns:
        Detailed game analysis
    """
    if not request.api_key:
        return GameAnalysisResponse(
            success=False,
            error="API key is required"
        )

    if not request.pgn_data:
        return GameAnalysisResponse(
            success=False,
            error="PGN data is required"
        )

    # Create LLM provider
    llm_provider = create_llm_provider(
        provider=request.provider,
        api_key=request.api_key
    )

    if not llm_provider:
        return GameAnalysisResponse(
            success=False,
            error=f"Invalid LLM provider: {request.provider}"
        )

    # Try to create chess engine (optional)
    chess_engine = None
    try:
        engine = StockfishAdapter()
        if engine.is_available():
            chess_engine = engine
    except Exception as e:
        logger.warning(f"Stockfish not available: {e}")

    # Create analysis service
    analysis_service = MoveAnalysisService(llm_provider, chess_engine)

    try:
        result = analysis_service.analyze_game(request.pgn_data)

        return GameAnalysisResponse(
            success=True,
            summary=result.get("summary"),
            critical_moments=result.get("critical_moments", []),
            mistakes=result.get("mistakes", []),
            blunders=result.get("blunders", []),
            recommendations=result.get("recommendations", [])
        )

    except ValueError as e:
        return GameAnalysisResponse(
            success=False,
            error=str(e)
        )
    except Exception as e:
        logger.error(f"Game analysis error: {e}")
        return GameAnalysisResponse(
            success=False,
            error=f"Analysis failed: {str(e)}"
        )
