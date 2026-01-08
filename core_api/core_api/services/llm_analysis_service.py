"""LLM-based chess game analysis service."""

import httpx
from typing import List, Optional
from pydantic import BaseModel
import logging
from datetime import datetime

from core_api.services.chesscom_service import ChessComGame

logger = logging.getLogger(__name__)

ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"


class GameTrendAnalysis(BaseModel):
    """Analysis results for game trends."""
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


class LLMAnalysisError(Exception):
    """Exception raised for LLM analysis errors."""
    pass


class LLMAnalysisService:
    """Service for analyzing chess games using LLM."""

    def __init__(self, api_key: str):
        """Initialize the LLM analysis service.

        Args:
            api_key: Anthropic API key for Claude
        """
        self.api_key = api_key
        self.client = httpx.Client(timeout=120.0)

    def _prepare_games_summary(self, games: List[ChessComGame], username: str) -> str:
        """Prepare a summary of games for analysis."""
        summary_lines = []

        # Calculate statistics
        total_games = len(games)
        wins = 0
        losses = 0
        draws = 0
        openings = {}
        time_classes = {}

        for game in games:
            # Determine if the user was white or black
            is_white = game.white_username.lower() == username.lower()

            if is_white:
                result = game.white_result
                user_rating = game.white_rating
                opponent_rating = game.black_rating
                opponent_name = game.black_username
            else:
                result = game.black_result
                user_rating = game.black_rating
                opponent_rating = game.white_rating
                opponent_name = game.white_username

            # Count results
            if result == "win":
                wins += 1
            elif result in ["checkmated", "timeout", "resigned", "abandoned"]:
                losses += 1
            else:
                draws += 1

            # Track openings
            if game.opening:
                openings[game.opening] = openings.get(game.opening, 0) + 1

            # Track time classes
            time_classes[game.time_class] = time_classes.get(game.time_class, 0) + 1

            # Create game summary
            game_date = datetime.fromtimestamp(game.end_time).strftime("%Y-%m-%d")
            color = "White" if is_white else "Black"
            summary_lines.append(
                f"- {game_date}: Played as {color} vs {opponent_name} ({opponent_rating}). "
                f"Result: {result}. Opening: {game.opening or 'Unknown'}. "
                f"Time control: {game.time_class} ({game.time_control})"
            )

        # Build the full summary
        win_rate = (wins / total_games * 100) if total_games > 0 else 0
        top_openings = sorted(openings.items(), key=lambda x: x[1], reverse=True)[:5]

        header = f"""
Chess.com Game Analysis for: {username}
=====================================
Total games analyzed: {total_games}
Record: {wins} wins, {losses} losses, {draws} draws
Win rate: {win_rate:.1f}%

Most played openings:
{chr(10).join(f"  - {op}: {count} games" for op, count in top_openings)}

Time controls played:
{chr(10).join(f"  - {tc}: {count} games" for tc, count in time_classes.items())}

Individual game summaries:
{chr(10).join(summary_lines)}
"""
        return header, win_rate, [op for op, _ in top_openings]

    def analyze_games(self, games: List[ChessComGame], username: str) -> GameTrendAnalysis:
        """Analyze a set of chess games and provide trend analysis.

        Args:
            games: List of games to analyze
            username: Chess.com username

        Returns:
            GameTrendAnalysis with insights and recommendations
        """
        if not games:
            raise LLMAnalysisError("No games provided for analysis")

        if not self.api_key:
            raise LLMAnalysisError("API key not configured")

        # Prepare the games summary
        games_summary, win_rate, top_openings = self._prepare_games_summary(games, username)

        # Create the prompt for Claude
        prompt = f"""You are an expert chess coach analyzing a player's recent games. Based on the following game data, provide a comprehensive analysis of their playing trends, strengths, weaknesses, and recommendations for improvement.

{games_summary}

Please provide your analysis in the following JSON format:
{{
    "summary": "A 2-3 sentence overall assessment of the player's recent performance",
    "strengths": ["strength1", "strength2", "strength3"],
    "weaknesses": ["weakness1", "weakness2", "weakness3"],
    "opening_trends": "Analysis of their opening play and repertoire choices",
    "time_management": "Assessment of how they handle different time controls",
    "recommendations": ["recommendation1", "recommendation2", "recommendation3", "recommendation4", "recommendation5"]
}}

Focus on actionable insights. Be specific about patterns you observe. Consider:
- Win/loss patterns (do they win more as white or black?)
- Opening choices and their success rates
- Performance in different time controls
- Areas that need the most improvement

Return ONLY the JSON object, no additional text."""

        try:
            response = self.client.post(
                ANTHROPIC_API_URL,
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                },
                json={
                    "model": "claude-sonnet-4-20250514",
                    "max_tokens": 2048,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ]
                }
            )

            if response.status_code == 401:
                raise LLMAnalysisError("Invalid API key. Please check your Anthropic API key.")
            elif response.status_code == 429:
                raise LLMAnalysisError("Rate limit exceeded. Please try again later.")
            elif response.status_code != 200:
                raise LLMAnalysisError(f"API request failed with status {response.status_code}")

            result = response.json()

            # Extract the text content from Claude's response
            content = result.get("content", [])
            if not content:
                raise LLMAnalysisError("Empty response from LLM")

            text_content = content[0].get("text", "")

            # Parse the JSON response
            import json
            try:
                # Try to find JSON in the response
                json_start = text_content.find("{")
                json_end = text_content.rfind("}") + 1
                if json_start != -1 and json_end > json_start:
                    analysis_data = json.loads(text_content[json_start:json_end])
                else:
                    raise LLMAnalysisError("Could not find JSON in LLM response")
            except json.JSONDecodeError as e:
                raise LLMAnalysisError(f"Failed to parse LLM response: {e}")

            return GameTrendAnalysis(
                username=username,
                games_analyzed=len(games),
                analysis_date=datetime.now().isoformat(),
                summary=analysis_data.get("summary", "Analysis not available"),
                strengths=analysis_data.get("strengths", []),
                weaknesses=analysis_data.get("weaknesses", []),
                opening_trends=analysis_data.get("opening_trends", ""),
                time_management=analysis_data.get("time_management", ""),
                recommendations=analysis_data.get("recommendations", []),
                win_rate=win_rate,
                most_played_openings=top_openings
            )

        except httpx.HTTPError as e:
            raise LLMAnalysisError(f"HTTP error during analysis: {e}")
        except LLMAnalysisError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error during LLM analysis: {e}")
            raise LLMAnalysisError(f"Analysis failed: {e}")

    def close(self):
        """Close the HTTP client."""
        self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
