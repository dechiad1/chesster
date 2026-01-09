"""Chess coach service for interactive coaching."""

import json
import logging
import re
from typing import List, Optional, Dict, Any

import chess

from core_api.domain.ports.llm_port import LLMProviderPort, Message
from core_api.domain.ports.chess_engine_port import ChessEnginePort

logger = logging.getLogger(__name__)

COACH_SYSTEM_PROMPT = """You are an expert chess coach helping a student improve their game. Your role is to:

1. Answer questions about chess strategy, tactics, and concepts
2. Analyze the current position when asked
3. Explain ideas behind moves and plans
4. Help the student learn from their mistakes
5. Provide encouragement while being honest about areas for improvement

When discussing positions:
- Use proper chess notation (e4, Nf3, etc.)
- Explain concepts in terms the student can understand
- Point out tactical and strategic themes
- Suggest what to look for in similar positions

Be supportive but educational. Your goal is to help the student grow as a chess player.

Current game context will be provided with each message."""


class CoachService:
    """Service for chess coaching interactions."""

    def __init__(
        self,
        llm_provider: LLMProviderPort,
        chess_engine: Optional[ChessEnginePort] = None
    ):
        """Initialize the coach service.

        Args:
            llm_provider: LLM provider for generating responses
            chess_engine: Optional chess engine for position analysis
        """
        self._llm = llm_provider
        self._engine = chess_engine

    def chat(
        self,
        message: str,
        fen: str,
        move_history: List[str],
        conversation_history: Optional[List[dict]] = None
    ) -> Dict[str, Any]:
        """Process a chat message from the user.

        Args:
            message: User's question or message
            fen: Current board position in FEN
            move_history: List of moves played (SAN notation)
            conversation_history: Previous messages in the conversation

        Returns:
            Dict with response_type, content, and optional lines
        """
        # Check if user is requesting line suggestions
        if self._is_requesting_lines(message):
            return self._generate_lines_response(fen, move_history, message)

        # Regular text response
        # Build context about the current position
        context = self._build_context(fen, move_history)

        # Add engine analysis if available
        if self._engine and self._engine.is_available():
            try:
                analysis = self._engine.analyze_position(fen, depth=15)
                context += f"\n\nEngine evaluation: {analysis.evaluation / 100:.2f} (positive = white advantage)"
                context += f"\nBest move according to engine: {analysis.best_move}"
            except Exception as e:
                logger.warning(f"Engine analysis failed: {e}")

        # Build messages
        messages = []

        # Add conversation history
        if conversation_history:
            for msg in conversation_history[-10:]:  # Keep last 10 messages
                messages.append(Message(
                    role=msg.get("role", "user"),
                    content=msg.get("content", "")
                ))

        # Add current message with context
        user_message = f"""[Current Position Context]
{context}

[User Question]
{message}"""

        messages.append(Message(role="user", content=user_message))

        # Get response from LLM
        try:
            response = self._llm.chat(
                messages=messages,
                system_prompt=COACH_SYSTEM_PROMPT,
                max_tokens=1024
            )
            return {
                "response_type": "text",
                "content": response.content,
                "lines": None
            }
        except Exception as e:
            logger.error(f"Coach chat failed: {e}")
            raise

    def _build_context(self, fen: str, move_history: List[str]) -> str:
        """Build context string about the current position.

        Args:
            fen: Current FEN
            move_history: List of moves

        Returns:
            Context string
        """
        context_parts = [f"Current position (FEN): {fen}"]

        if move_history:
            # Format move history in standard notation
            formatted_moves = []
            for i, move in enumerate(move_history):
                move_num = i // 2 + 1
                if i % 2 == 0:
                    formatted_moves.append(f"{move_num}. {move}")
                else:
                    formatted_moves[-1] += f" {move}"

            context_parts.append(f"Moves played: {' '.join(formatted_moves)}")
            context_parts.append(f"Total moves: {len(move_history)}")

            # Determine whose turn it is
            turn = "White" if len(move_history) % 2 == 0 else "Black"
            context_parts.append(f"To move: {turn}")

        return "\n".join(context_parts)

    def get_position_advice(self, fen: str, move_history: List[str]) -> str:
        """Get proactive advice about the current position.

        Args:
            fen: Current FEN
            move_history: List of moves

        Returns:
            Advice text
        """
        context = self._build_context(fen, move_history)

        message = Message(
            role="user",
            content=f"""[Position for Analysis]
{context}

Please provide a brief assessment of this position. Consider:
1. What are the key features of this position?
2. What should the side to move be thinking about?
3. Are there any tactical or strategic ideas to consider?

Keep your response concise but educational."""
        )

        try:
            response = self._llm.chat(
                messages=[message],
                system_prompt=COACH_SYSTEM_PROMPT,
                max_tokens=512
            )
            return response.content
        except Exception as e:
            logger.error(f"Position advice failed: {e}")
            raise

    def _is_requesting_lines(self, message: str) -> bool:
        """Detect if user is asking for line/variation suggestions.

        Args:
            message: User's message

        Returns:
            True if requesting lines
        """
        keywords = [
            "continuation", "variations", "lines", "what should i play",
            "show me moves", "typical moves", "best continuations",
            "what are my options", "possible moves", "suggest moves",
            "show continuations", "what to play"
        ]
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in keywords)

    def _generate_lines_response(
        self,
        fen: str,
        move_history: List[str],
        message: str
    ) -> Dict[str, Any]:
        """Generate response with suggested chess lines.

        Args:
            fen: Current FEN
            move_history: Move history
            message: User's message

        Returns:
            Dict with lines response
        """
        if not self._engine or not self._engine.is_available():
            # No engine available, return text response
            return {
                "response_type": "text",
                "content": "I'd love to suggest specific lines, but I don't have access to a chess engine at the moment. I can still discuss general ideas and plans if you'd like!",
                "lines": None
            }

        try:
            # Get lines from engine analysis
            lines = self._generate_lines_from_engine(fen)

            if not lines:
                return {
                    "response_type": "text",
                    "content": "I couldn't generate specific variations for this position. Could you ask about a specific aspect of the position instead?",
                    "lines": None
                }

            return {
                "response_type": "lines",
                "content": "Here are some typical continuations to consider:",
                "lines": lines
            }

        except Exception as e:
            logger.error(f"Failed to generate lines: {e}")
            return {
                "response_type": "text",
                "content": "I encountered an error while analyzing variations. Please try asking in a different way.",
                "lines": None
            }

    def _generate_lines_from_engine(self, fen: str) -> List[Dict[str, Any]]:
        """Generate suggested lines using chess engine.

        Args:
            fen: Current FEN position

        Returns:
            List of line dicts with description, moves, moves_san, evaluation
        """
        try:
            board = chess.Board(fen)
        except Exception as e:
            logger.error(f"Invalid FEN: {e}")
            return []

        lines = []

        try:
            # Get top 3 variations using MultiPV
            logger.info(f"Requesting 3 lines for position: {fen}")
            analyses = self._engine.get_multiple_lines(fen, num_lines=3, depth=20)
            logger.info(f"Received {len(analyses)} analyses from engine")

            for i, analysis in enumerate(analyses):
                if not analysis or not analysis.pv:
                    continue

                # Get the principal variation (first few moves)
                pv_moves = analysis.pv[:5]  # Take first 5 moves of the line

                if not pv_moves:
                    continue

                # Convert to SAN notation for display
                temp_board = board.copy()
                moves_uci = []
                moves_san = []

                for move_uci in pv_moves:
                    try:
                        move = chess.Move.from_uci(move_uci)
                        if move in temp_board.legal_moves:
                            moves_uci.append(move_uci)
                            moves_san.append(temp_board.san(move))
                            temp_board.push(move)
                        else:
                            break
                    except Exception as e:
                        logger.warning(f"Invalid move in PV: {move_uci}, {e}")
                        break

                if not moves_uci:
                    continue

                # Generate description based on line characteristics
                description = self._generate_line_description(board, moves_san, i + 1)

                lines.append({
                    "description": description,
                    "moves": moves_uci,
                    "moves_san": moves_san,
                    "evaluation": analysis.evaluation
                })

        except Exception as e:
            logger.error(f"Failed to generate lines: {e}")
            return []

        return lines

    def _generate_line_description(
        self,
        board: chess.Board,
        moves_san: List[str],
        line_number: int
    ) -> str:
        """Generate a description for a chess line.

        Args:
            board: Starting board position
            moves_san: Moves in SAN notation
            line_number: Which line this is (1, 2, or 3)

        Returns:
            Description string
        """
        descriptions = {
            1: "Engine's top recommendation",
            2: "Strong alternative line",
            3: "Another solid continuation"
        }

        base_desc = descriptions.get(line_number, "Interesting variation")

        # Add context based on first move characteristics
        if moves_san:
            first_move = moves_san[0]

            # Check if it's a capture
            if 'x' in first_move:
                base_desc += " (captures material)"
            # Check if it's a check
            elif '+' in first_move or '#' in first_move:
                base_desc += " (gives check)"
            # Check for castling
            elif first_move in ('O-O', 'O-O-O'):
                base_desc += " (castling)"

        return base_desc
