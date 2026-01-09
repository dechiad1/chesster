"""Stockfish chess engine adapter."""

import logging
import shutil
from typing import Optional

import chess

from core_api.domain.ports.chess_engine_port import (
    ChessEnginePort,
    PositionAnalysis,
    MoveEvaluation
)

logger = logging.getLogger(__name__)


class StockfishAdapter(ChessEnginePort):
    """Stockfish chess engine adapter.

    Uses python-chess's built-in engine support.
    """

    def __init__(self, path: Optional[str] = None, depth: int = 20):
        """Initialize the Stockfish adapter.

        Args:
            path: Path to Stockfish binary (auto-detected if None)
            depth: Default analysis depth
        """
        self._path = path or self._find_stockfish()
        self._default_depth = depth
        self._engine: Optional[chess.engine.SimpleEngine] = None

    def _find_stockfish(self) -> Optional[str]:
        """Find Stockfish binary in system PATH."""
        for name in ['stockfish', 'stockfish.exe']:
            path = shutil.which(name)
            if path:
                return path
        return None

    def _get_engine(self) -> chess.engine.SimpleEngine:
        """Get or create the engine instance."""
        if self._engine is None:
            if not self._path:
                raise ValueError("Stockfish not found. Please install Stockfish.")
            self._engine = chess.engine.SimpleEngine.popen_uci(self._path)
        return self._engine

    def analyze_position(self, fen: str, depth: int = 20) -> PositionAnalysis:
        """Analyze a chess position.

        Args:
            fen: Position in FEN notation
            depth: Search depth

        Returns:
            PositionAnalysis with evaluation and best move
        """
        engine = self._get_engine()
        board = chess.Board(fen)

        info = engine.analyse(board, chess.engine.Limit(depth=depth or self._default_depth))

        score = info.get("score", chess.engine.PovScore(chess.engine.Cp(0), chess.WHITE))
        pov_score = score.white()

        # Handle mate scores
        is_mate = pov_score.is_mate()
        mate_in = pov_score.mate() if is_mate else None

        # Convert to centipawns
        if is_mate:
            evaluation = 10000 if mate_in > 0 else -10000
        else:
            evaluation = pov_score.score() or 0

        # Get best move and PV
        pv = info.get("pv", [])
        best_move = pv[0].uci() if pv else ""
        pv_uci = [move.uci() for move in pv]

        return PositionAnalysis(
            fen=fen,
            evaluation=evaluation,
            best_move=best_move,
            depth=info.get("depth", depth),
            pv=pv_uci,
            is_mate=is_mate,
            mate_in=mate_in
        )

    def evaluate_move(self, fen: str, move: str, depth: int = 20) -> MoveEvaluation:
        """Evaluate a specific move.

        Args:
            fen: Position before the move (FEN)
            move: The move to evaluate (UCI)
            depth: Search depth

        Returns:
            MoveEvaluation with centipawn loss and classification
        """
        engine = self._get_engine()
        board = chess.Board(fen)

        # Analyze position before move
        info_before = engine.analyse(board, chess.engine.Limit(depth=depth))
        score_before = info_before.get("score", chess.engine.PovScore(chess.engine.Cp(0), chess.WHITE))
        eval_before = self._score_to_cp(score_before.white())

        # Get the best move
        pv = info_before.get("pv", [])
        best_move = pv[0].uci() if pv else move

        # Make the move
        try:
            chess_move = chess.Move.from_uci(move)
            if chess_move not in board.legal_moves:
                raise ValueError(f"Illegal move: {move}")
            board.push(chess_move)
        except Exception as e:
            raise ValueError(f"Invalid move: {move} - {e}")

        # Analyze position after move
        info_after = engine.analyse(board, chess.engine.Limit(depth=depth))
        score_after = info_after.get("score", chess.engine.PovScore(chess.engine.Cp(0), chess.WHITE))
        eval_after = self._score_to_cp(score_after.white())

        # Calculate centipawn loss (from the perspective of the moving side)
        # If it was white's turn, we compare white's evaluation
        # Negative eval_after means white is worse after the move
        was_white_turn = not board.turn  # After push, turn has changed
        if was_white_turn:
            cp_loss = eval_before - (-eval_after)  # Negate because we're now from black's view
        else:
            cp_loss = (-eval_before) - eval_after  # From black's perspective originally

        cp_loss = max(0, cp_loss)  # Loss should be non-negative

        # Get best move evaluation
        best_move_eval = eval_before

        return MoveEvaluation(
            move=move,
            evaluation_before=eval_before,
            evaluation_after=-eval_after if was_white_turn else eval_after,
            centipawn_loss=cp_loss,
            is_blunder=cp_loss > 200,
            is_mistake=100 < cp_loss <= 200,
            is_inaccuracy=50 < cp_loss <= 100,
            best_move=best_move,
            best_move_eval=best_move_eval
        )

    def _score_to_cp(self, score: chess.engine.Score) -> float:
        """Convert engine score to centipawns."""
        if score.is_mate():
            mate = score.mate()
            return 10000 if mate > 0 else -10000
        return score.score() or 0

    def get_best_move(self, fen: str, depth: int = 20) -> str:
        """Get the best move for a position.

        Args:
            fen: Position in FEN notation
            depth: Search depth

        Returns:
            Best move in UCI format
        """
        engine = self._get_engine()
        board = chess.Board(fen)

        result = engine.play(board, chess.engine.Limit(depth=depth or self._default_depth))
        return result.move.uci() if result.move else ""

    def get_multiple_lines(self, fen: str, num_lines: int = 3, depth: int = 20) -> list[PositionAnalysis]:
        """Get multiple principal variations for a position.

        Args:
            fen: Position in FEN notation
            num_lines: Number of variations to get (default 3)
            depth: Search depth

        Returns:
            List of PositionAnalysis objects, one for each variation
        """
        logger.info(f"Getting {num_lines} lines for position")
        try:
            engine = self._get_engine()
            board = chess.Board(fen)

            # Analyze with MultiPV - python-chess manages MultiPV automatically via the multipv parameter
            logger.info(f"Starting engine analysis with MultiPV={num_lines}...")
            infos = engine.analyse(board, chess.engine.Limit(depth=depth or self._default_depth), multipv=num_lines)
            logger.info(f"Analysis complete, received {len(infos) if isinstance(infos, list) else 1} results")
        except Exception as e:
            logger.error(f"Error during engine analysis: {e}", exc_info=True)
            return []

        results = []
        for info in infos:
            score = info.get("score", chess.engine.PovScore(chess.engine.Cp(0), chess.WHITE))
            pov_score = score.white()

            # Handle mate scores
            is_mate = pov_score.is_mate()
            mate_in = pov_score.mate() if is_mate else None

            # Convert to centipawns
            if is_mate:
                evaluation = 10000 if mate_in > 0 else -10000
            else:
                evaluation = pov_score.score() or 0

            # Get PV for this variation
            pv = info.get("pv", [])
            best_move = pv[0].uci() if pv else ""
            pv_uci = [move.uci() for move in pv]

            results.append(PositionAnalysis(
                fen=fen,
                evaluation=evaluation,
                best_move=best_move,
                depth=info.get("depth", depth),
                pv=pv_uci,
                is_mate=is_mate,
                mate_in=mate_in
            ))

        return results

    def is_available(self) -> bool:
        """Check if Stockfish is available."""
        if not self._path:
            return False
        try:
            engine = self._get_engine()
            return engine is not None
        except Exception:
            return False

    def close(self):
        """Close the engine."""
        if self._engine:
            self._engine.quit()
            self._engine = None
