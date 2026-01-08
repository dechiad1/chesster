"""Chess coach service for interactive coaching."""

import logging
from typing import List, Optional

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
    ) -> str:
        """Process a chat message from the user.

        Args:
            message: User's question or message
            fen: Current board position in FEN
            move_history: List of moves played (SAN notation)
            conversation_history: Previous messages in the conversation

        Returns:
            Coach's response text
        """
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
            return response.content
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
