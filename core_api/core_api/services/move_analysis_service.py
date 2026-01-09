"""Move-by-move game analysis service."""

import logging
import re
from typing import List, Optional, Dict, Any

import chess
import chess.pgn
import io

from core_api.domain.ports.llm_port import LLMProviderPort, Message
from core_api.domain.ports.chess_engine_port import ChessEnginePort, MoveEvaluation

logger = logging.getLogger(__name__)

ANALYSIS_SYSTEM_PROMPT = """You are an expert chess analyst providing detailed game analysis. Your task is to:

1. Identify the critical moments in the game (turning points, mistakes, blunders)
2. Explain why certain moves were mistakes and what would have been better
3. Highlight any tactical or strategic themes
4. Provide actionable recommendations for improvement

Focus on the most instructive moments rather than analyzing every move.
Be specific and educational in your explanations.

When providing analysis, format your response as JSON with the following structure:
{
    "summary": "Overall assessment of the game (2-3 sentences)",
    "critical_moments": [
        {"move_number": 15, "description": "The position changed dramatically after..."}
    ],
    "mistakes": [
        {"move_number": 23, "move": "Qxd4", "explanation": "This loses material because...", "better_move": "Nc6"}
    ],
    "blunders": [
        {"move_number": 31, "move": "Rxe4", "explanation": "This hangs the queen...", "better_move": "Qf3"}
    ],
    "recommendations": ["Work on endgame technique", "Study tactical patterns"]
}"""


class MoveAnalysisService:
    """Service for analyzing chess games move-by-move."""

    def __init__(
        self,
        llm_provider: LLMProviderPort,
        chess_engine: Optional[ChessEnginePort] = None
    ):
        """Initialize the analysis service.

        Args:
            llm_provider: LLM provider for generating analysis
            chess_engine: Optional chess engine for objective evaluation
        """
        self._llm = llm_provider
        self._engine = chess_engine

    def analyze_game(self, pgn_data: str) -> Dict[str, Any]:
        """Analyze a complete game.

        Args:
            pgn_data: PGN notation of the game

        Returns:
            Dictionary with analysis results
        """
        # Parse the PGN
        game_info = self._parse_pgn(pgn_data)

        if not game_info:
            raise ValueError("Failed to parse PGN data")

        # If we have an engine, do move-by-move evaluation
        engine_analysis = None
        if self._engine and self._engine.is_available():
            try:
                engine_analysis = self._engine_analyze_game(game_info["moves"], game_info["fens"])
            except Exception as e:
                logger.warning(f"Engine analysis failed: {e}")

        # Build the prompt for LLM analysis
        analysis_prompt = self._build_analysis_prompt(game_info, engine_analysis)

        # Get LLM analysis
        message = Message(role="user", content=analysis_prompt)

        try:
            response = self._llm.chat(
                messages=[message],
                system_prompt=ANALYSIS_SYSTEM_PROMPT,
                max_tokens=2048
            )

            # Parse the JSON response
            return self._parse_analysis_response(response.content)

        except Exception as e:
            logger.error(f"Game analysis failed: {e}")
            raise

    def _parse_pgn(self, pgn_data: str) -> Optional[Dict[str, Any]]:
        """Parse PGN data and extract game information.

        Args:
            pgn_data: PGN string

        Returns:
            Dictionary with game info or None
        """
        try:
            pgn_io = io.StringIO(pgn_data)
            game = chess.pgn.read_game(pgn_io)

            if not game:
                return None

            # Extract headers
            headers = dict(game.headers)

            # Extract moves and positions
            moves = []
            fens = []
            board = game.board()
            fens.append(board.fen())

            for move in game.mainline_moves():
                moves.append(board.san(move))
                board.push(move)
                fens.append(board.fen())

            return {
                "headers": headers,
                "moves": moves,
                "fens": fens,
                "result": headers.get("Result", "*"),
                "white": headers.get("White", "Unknown"),
                "black": headers.get("Black", "Unknown"),
                "opening": headers.get("Opening", headers.get("ECO", "Unknown"))
            }

        except Exception as e:
            logger.error(f"PGN parsing failed: {e}")
            return None

    def _engine_analyze_game(
        self,
        moves: List[str],
        fens: List[str]
    ) -> List[Dict[str, Any]]:
        """Analyze all moves with the chess engine.

        Args:
            moves: List of moves in SAN
            fens: List of positions (FEN) before each move

        Returns:
            List of move evaluations
        """
        evaluations = []

        for i, (move, fen) in enumerate(zip(moves, fens[:-1])):
            try:
                # Convert SAN to UCI
                board = chess.Board(fen)
                chess_move = board.parse_san(move)
                uci_move = chess_move.uci()

                eval_result = self._engine.evaluate_move(fen, uci_move, depth=15)
                evaluations.append({
                    "move_number": i // 2 + 1,
                    "color": "white" if i % 2 == 0 else "black",
                    "move": move,
                    "centipawn_loss": eval_result.centipawn_loss,
                    "is_blunder": eval_result.is_blunder,
                    "is_mistake": eval_result.is_mistake,
                    "is_inaccuracy": eval_result.is_inaccuracy,
                    "best_move": eval_result.best_move,
                    "evaluation": eval_result.evaluation_after
                })

            except Exception as e:
                logger.warning(f"Failed to evaluate move {i + 1}: {e}")

        return evaluations

    def _build_analysis_prompt(
        self,
        game_info: Dict[str, Any],
        engine_analysis: Optional[List[Dict[str, Any]]]
    ) -> str:
        """Build the analysis prompt for the LLM.

        Args:
            game_info: Parsed game information
            engine_analysis: Optional engine evaluations

        Returns:
            Prompt string
        """
        prompt_parts = [
            f"Please analyze the following chess game:\n",
            f"White: {game_info['white']}",
            f"Black: {game_info['black']}",
            f"Result: {game_info['result']}",
            f"Opening: {game_info['opening']}\n",
            "Moves:"
        ]

        # Format moves in standard notation
        moves = game_info["moves"]
        formatted_moves = []
        for i in range(0, len(moves), 2):
            move_num = i // 2 + 1
            white_move = moves[i]
            black_move = moves[i + 1] if i + 1 < len(moves) else ""
            if black_move:
                formatted_moves.append(f"{move_num}. {white_move} {black_move}")
            else:
                formatted_moves.append(f"{move_num}. {white_move}")

        prompt_parts.append(" ".join(formatted_moves))

        # Add engine analysis if available
        if engine_analysis:
            blunders = [e for e in engine_analysis if e["is_blunder"]]
            mistakes = [e for e in engine_analysis if e["is_mistake"]]

            if blunders or mistakes:
                prompt_parts.append("\n\nEngine-identified issues:")

                for b in blunders:
                    color = b["color"].title()
                    prompt_parts.append(
                        f"- Move {b['move_number']} ({color}): {b['move']} is a BLUNDER "
                        f"(lost {b['centipawn_loss']:.0f} centipawns, better was {b['best_move']})"
                    )

                for m in mistakes:
                    color = m["color"].title()
                    prompt_parts.append(
                        f"- Move {m['move_number']} ({color}): {m['move']} is a mistake "
                        f"(lost {m['centipawn_loss']:.0f} centipawns, better was {m['best_move']})"
                    )

        prompt_parts.append(
            "\n\nPlease provide your analysis in the JSON format specified. "
            "Focus on the most instructive moments and provide clear explanations."
        )

        return "\n".join(prompt_parts)

    def _parse_analysis_response(self, response: str) -> Dict[str, Any]:
        """Parse the LLM analysis response.

        Args:
            response: LLM response text

        Returns:
            Parsed analysis dictionary
        """
        import json

        # Try to extract JSON from response
        try:
            # Find JSON in the response
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass

        # If JSON parsing fails, return the raw response
        return {
            "summary": response[:500] if len(response) > 500 else response,
            "critical_moments": [],
            "mistakes": [],
            "blunders": [],
            "recommendations": [],
            "raw_analysis": response
        }
