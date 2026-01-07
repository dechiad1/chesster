"""Schemas for chess.com integration and LLM analysis."""

from typing import List, Optional
from pydantic import BaseModel


class ChessComGameSchema(BaseModel):
    """Chess.com game schema for API responses."""
    url: str
    pgn: str
    time_control: str
    end_time: int
    rated: bool
    time_class: str
    rules: str
    white_username: str
    white_rating: int
    white_result: str
    black_username: str
    black_rating: int
    black_result: str
    opening: Optional[str] = None


class ChessComProfileSchema(BaseModel):
    """Chess.com player profile schema."""
    username: str
    player_id: int
    url: str
    country: Optional[str] = None
    joined: int
    last_online: int
    followers: int
    is_streamer: bool


class FetchGamesRequest(BaseModel):
    """Request schema for fetching chess.com games."""
    username: str
    count: int = 15


class FetchGamesResponse(BaseModel):
    """Response schema for fetched games."""
    username: str
    games_count: int
    games: List[ChessComGameSchema]


class AnalyzeGamesRequest(BaseModel):
    """Request schema for analyzing games with LLM."""
    username: str
    api_key: str
    count: int = 15


class GameTrendAnalysisSchema(BaseModel):
    """Schema for game trend analysis results."""
    username: str
    games_analyzed: int
    analysis_date: str
    summary: str
    strengths: List[str]
    weaknesses: List[str]
    opening_trends: str
    time_management: str
    recommendations: List[str]
    win_rate: float
    most_played_openings: List[str]


class AnalyzeGamesResponse(BaseModel):
    """Response schema for game analysis."""
    success: bool
    analysis: Optional[GameTrendAnalysisSchema] = None
    error: Optional[str] = None
