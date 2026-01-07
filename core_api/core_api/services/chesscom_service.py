"""Chess.com API integration service."""

import httpx
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

CHESSCOM_API_BASE = "https://api.chess.com/pub"


class ChessComGame(BaseModel):
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


class ChessComProfile(BaseModel):
    """Chess.com player profile."""
    username: str
    player_id: int
    url: str
    country: Optional[str] = None
    joined: int
    last_online: int
    followers: int
    is_streamer: bool


class ChessComServiceError(Exception):
    """Exception raised for chess.com API errors."""
    pass


class ChessComService:
    """Service for interacting with the Chess.com public API."""

    def __init__(self):
        self.client = httpx.Client(
            timeout=30.0,
            headers={
                "User-Agent": "Chesster/1.0 (Chess Analysis App)"
            }
        )

    def get_player_profile(self, username: str) -> ChessComProfile:
        """Get a player's profile from Chess.com."""
        try:
            response = self.client.get(f"{CHESSCOM_API_BASE}/player/{username}")
            response.raise_for_status()
            data = response.json()

            return ChessComProfile(
                username=data.get("username", username),
                player_id=data.get("player_id", 0),
                url=data.get("url", ""),
                country=data.get("country"),
                joined=data.get("joined", 0),
                last_online=data.get("last_online", 0),
                followers=data.get("followers", 0),
                is_streamer=data.get("is_streamer", False)
            )
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise ChessComServiceError(f"Player '{username}' not found on Chess.com")
            raise ChessComServiceError(f"Failed to fetch profile: {e}")
        except Exception as e:
            raise ChessComServiceError(f"Error fetching profile: {e}")

    def get_player_game_archives(self, username: str) -> List[str]:
        """Get list of monthly game archive URLs for a player."""
        try:
            response = self.client.get(f"{CHESSCOM_API_BASE}/player/{username}/games/archives")
            response.raise_for_status()
            data = response.json()
            return data.get("archives", [])
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise ChessComServiceError(f"Player '{username}' not found on Chess.com")
            raise ChessComServiceError(f"Failed to fetch archives: {e}")
        except Exception as e:
            raise ChessComServiceError(f"Error fetching archives: {e}")

    def get_games_from_archive(self, archive_url: str) -> List[ChessComGame]:
        """Get games from a specific monthly archive."""
        try:
            response = self.client.get(archive_url)
            response.raise_for_status()
            data = response.json()

            games = []
            for game_data in data.get("games", []):
                try:
                    # Extract opening from PGN if available
                    pgn = game_data.get("pgn", "")
                    opening = None
                    for line in pgn.split("\n"):
                        if line.startswith("[ECOUrl"):
                            # Extract opening name from ECOUrl
                            opening = line.split("/")[-1].strip('"]').replace("-", " ")
                            break
                        elif line.startswith("[Opening"):
                            opening = line.split('"')[1] if '"' in line else None
                            break

                    game = ChessComGame(
                        url=game_data.get("url", ""),
                        pgn=pgn,
                        time_control=game_data.get("time_control", ""),
                        end_time=game_data.get("end_time", 0),
                        rated=game_data.get("rated", False),
                        time_class=game_data.get("time_class", ""),
                        rules=game_data.get("rules", "chess"),
                        white_username=game_data.get("white", {}).get("username", ""),
                        white_rating=game_data.get("white", {}).get("rating", 0),
                        white_result=game_data.get("white", {}).get("result", ""),
                        black_username=game_data.get("black", {}).get("username", ""),
                        black_rating=game_data.get("black", {}).get("rating", 0),
                        black_result=game_data.get("black", {}).get("result", ""),
                        opening=opening
                    )
                    games.append(game)
                except Exception as e:
                    logger.warning(f"Failed to parse game: {e}")
                    continue

            return games
        except httpx.HTTPStatusError as e:
            raise ChessComServiceError(f"Failed to fetch games from archive: {e}")
        except Exception as e:
            raise ChessComServiceError(f"Error fetching games: {e}")

    def get_recent_games(self, username: str, count: int = 15) -> List[ChessComGame]:
        """Get the most recent games for a player.

        Args:
            username: Chess.com username
            count: Number of recent games to fetch (default 15)

        Returns:
            List of recent games, sorted from newest to oldest
        """
        try:
            # Get archives list (ordered oldest to newest)
            archives = self.get_player_game_archives(username)

            if not archives:
                return []

            # Start from most recent archive and work backwards
            all_games = []
            for archive_url in reversed(archives):
                games = self.get_games_from_archive(archive_url)
                # Sort by end_time descending (most recent first)
                games.sort(key=lambda g: g.end_time, reverse=True)
                all_games.extend(games)

                if len(all_games) >= count:
                    break

            # Return only the requested number of games
            return all_games[:count]

        except ChessComServiceError:
            raise
        except Exception as e:
            raise ChessComServiceError(f"Error fetching recent games: {e}")

    def close(self):
        """Close the HTTP client."""
        self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
