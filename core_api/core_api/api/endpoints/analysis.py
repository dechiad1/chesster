"""API endpoints for chess.com integration and LLM analysis."""

from fastapi import APIRouter, HTTPException
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
