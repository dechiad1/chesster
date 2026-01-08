"""API client for communicating with the chess platform backend."""

import httpx
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)


class APIError(Exception):
    """Custom exception for API errors."""
    pass


class GameData(BaseModel):
    """Game data model."""
    game_id: int
    white_player_id: Optional[int]
    black_player_id: Optional[int]
    start_datetime: Optional[str]
    end_datetime: Optional[str]
    result: Optional[str]
    pgn_data: str
    source: Optional[str]
    created_at: str


class UserData(BaseModel):
    """User data model."""
    user_id: int
    username: str
    email: str
    full_name: str
    nationality: Optional[str]
    avatar_path: Optional[str]
    rating: Optional[int]
    registration_date: str
    last_login_date: Optional[str]
    is_active: bool


class ChessComGameData(BaseModel):
    """Chess.com game data model."""
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


class GameTrendAnalysis(BaseModel):
    """Game trend analysis results."""
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


class ChessAPIClient:
    """Client for Chess Platform API."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api/v1"
        self.client = httpx.Client(timeout=30.0)
        
    def _handle_response(self, response: httpx.Response) -> Dict[str, Any]:
        """Handle API response and raise errors if needed."""
        try:
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            try:
                error_detail = response.json().get("detail", str(e))
            except Exception:
                error_detail = str(e)
            raise APIError(f"API error ({response.status_code}): {error_detail}") from e
        except Exception as e:
            raise APIError(f"Request failed: {str(e)}") from e
    
    def health_check(self) -> bool:
        """Check if the API server is running."""
        try:
            response = self.client.get(f"{self.base_url}/health")
            return response.status_code == 200
        except Exception:
            return False
    
    # Game Management
    def create_game(self, pgn_data: str, white_player_id: Optional[int] = None, 
                   black_player_id: Optional[int] = None, result: Optional[str] = None,
                   source: str = "desktop") -> GameData:
        """Create a new game."""
        data = {
            "pgn_data": pgn_data,
            "white_player_id": white_player_id,
            "black_player_id": black_player_id,
            "result": result,
            "source": source
        }
        response = self.client.post(f"{self.api_url}/games/", json=data)
        result = self._handle_response(response)
        return GameData(**result)
    
    def get_games(self, user_id: Optional[int] = None, skip: int = 0, 
                  limit: int = 100) -> List[GameData]:
        """Get list of games."""
        params = {"skip": skip, "limit": limit}
        if user_id:
            params["user_id"] = user_id
            
        response = self.client.get(f"{self.api_url}/games/", params=params)
        result = self._handle_response(response)
        return [GameData(**game) for game in result]
    
    def get_game(self, game_id: int) -> GameData:
        """Get a specific game."""
        response = self.client.get(f"{self.api_url}/games/{game_id}")
        result = self._handle_response(response)
        return GameData(**result)
    
    def update_game(self, game_id: int, **updates) -> GameData:
        """Update a game."""
        response = self.client.put(f"{self.api_url}/games/{game_id}", json=updates)
        result = self._handle_response(response)
        return GameData(**result)
    
    def delete_game(self, game_id: int) -> bool:
        """Delete a game."""
        response = self.client.delete(f"{self.api_url}/games/{game_id}")
        self._handle_response(response)
        return True
    
    def export_game_pgn(self, game_id: int) -> str:
        """Export game as PGN."""
        response = self.client.get(f"{self.api_url}/games/{game_id}/pgn")
        result = self._handle_response(response)
        return result["pgn"]
    
    def import_game_pgn(self, pgn_data: str) -> GameData:
        """Import a game from PGN."""
        data = {"pgn_data": pgn_data}
        response = self.client.post(f"{self.api_url}/games/import", json=data)
        result = self._handle_response(response)
        return GameData(**result)
    
    # Chess Operations
    def make_move(self, fen: str, move: str) -> Dict[str, Any]:
        """Make a move and get the result."""
        data = {"fen": fen, "move": move}
        response = self.client.post(f"{self.api_url}/chess/move", json=data)
        return self._handle_response(response)
    
    def analyze_position(self, fen: str) -> Dict[str, Any]:
        """Analyze a chess position."""
        data = {"fen": fen}
        response = self.client.post(f"{self.api_url}/chess/analyze", json=data)
        return self._handle_response(response)
    
    def validate_game(self, pgn: str) -> Dict[str, Any]:
        """Validate a PGN game."""
        data = {"pgn": pgn}
        response = self.client.post(f"{self.api_url}/chess/validate", json=data)
        return self._handle_response(response)
    
    def get_openings(self) -> Dict[str, str]:
        """Get available chess openings."""
        response = self.client.get(f"{self.api_url}/chess/openings")
        result = self._handle_response(response)
        return result["openings"]
    
    def get_opening_info(self, opening_name: str) -> Dict[str, Any]:
        """Get information about a specific opening."""
        response = self.client.get(f"{self.api_url}/chess/openings/{opening_name}")
        return self._handle_response(response)
    
    def get_starting_position(self) -> Dict[str, Any]:
        """Get the starting chess position."""
        response = self.client.get(f"{self.api_url}/chess/starting-position")
        return self._handle_response(response)
    
    # User Management (when auth is implemented)
    def create_user(self, username: str, email: str, full_name: str, 
                   password: str, **kwargs) -> UserData:
        """Create a new user."""
        data = {
            "username": username,
            "email": email,
            "full_name": full_name,
            "password": password,
            **kwargs
        }
        response = self.client.post(f"{self.api_url}/users/", json=data)
        result = self._handle_response(response)
        return UserData(**result)
    
    def get_user(self, user_id: int) -> UserData:
        """Get a user by ID."""
        response = self.client.get(f"{self.api_url}/users/{user_id}")
        result = self._handle_response(response)
        return UserData(**result)

    # Chess.com Integration
    def fetch_chesscom_games(self, username: str, count: int = 15) -> List[ChessComGameData]:
        """Fetch recent games from Chess.com for a player.

        Args:
            username: Chess.com username
            count: Number of games to fetch (default 15)

        Returns:
            List of recent games from Chess.com
        """
        data = {"username": username, "count": count}
        response = self.client.post(f"{self.api_url}/analysis/chesscom/games", json=data)
        result = self._handle_response(response)
        return [ChessComGameData(**game) for game in result.get("games", [])]

    def analyze_chesscom_games(
        self, username: str, api_key: str, count: int = 15
    ) -> Dict[str, Any]:
        """Analyze a player's Chess.com games using LLM.

        Args:
            username: Chess.com username
            api_key: Anthropic API key for LLM analysis
            count: Number of games to analyze (default 15)

        Returns:
            Dictionary with success status and analysis results
        """
        data = {"username": username, "api_key": api_key, "count": count}
        response = self.client.post(
            f"{self.api_url}/analysis/analyze",
            json=data,
            timeout=120.0  # Longer timeout for LLM analysis
        )
        return self._handle_response(response)

    def get_game_analysis(
        self, username: str, api_key: str, count: int = 15
    ) -> Optional[GameTrendAnalysis]:
        """Get trend analysis for a player's games.

        Args:
            username: Chess.com username
            api_key: Anthropic API key
            count: Number of games to analyze

        Returns:
            GameTrendAnalysis object or None if analysis failed
        """
        result = self.analyze_chesscom_games(username, api_key, count)
        if result.get("success") and result.get("analysis"):
            return GameTrendAnalysis(**result["analysis"])
        return None

    # Coach Chat
    def coach_chat(
        self,
        message: str,
        fen: str,
        move_history: List[str],
        provider: str = "anthropic",
        api_key: str = ""
    ) -> str:
        """Send a message to the chess coach.

        Args:
            message: User's message/question
            fen: Current board position in FEN
            move_history: List of moves in SAN notation
            provider: LLM provider name
            api_key: API key for the provider

        Returns:
            Coach's response text
        """
        data = {
            "message": message,
            "fen": fen,
            "move_history": move_history,
            "provider": provider,
            "api_key": api_key
        }
        response = self.client.post(
            f"{self.api_url}/coach/chat",
            json=data,
            timeout=60.0
        )
        result = self._handle_response(response)
        return result.get("response", "")

    # Game Analysis
    def analyze_game(
        self,
        game_id: int,
        pgn_data: str,
        provider: str = "anthropic",
        api_key: str = ""
    ) -> Dict[str, Any]:
        """Analyze a specific game for mistakes and blunders.

        Args:
            game_id: Game ID
            pgn_data: Full PGN of the game
            provider: LLM provider name
            api_key: API key for the provider

        Returns:
            Dictionary with analysis results
        """
        data = {
            "game_id": game_id,
            "pgn_data": pgn_data,
            "provider": provider,
            "api_key": api_key
        }
        response = self.client.post(
            f"{self.api_url}/analysis/game",
            json=data,
            timeout=120.0
        )
        return self._handle_response(response)

    def close(self):
        """Close the HTTP client."""
        self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()