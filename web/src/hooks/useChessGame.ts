import { useState, useCallback } from 'react';
import { Chess } from 'chess.js';

export interface ChessGameState {
  fen: string;
  moveHistory: string[]; // SAN notation
  currentMoveIndex: number;
  isGameOver: boolean;
  turn: 'w' | 'b';
}

export const useChessGame = () => {
  const [game] = useState(() => new Chess());
  const [gameState, setGameState] = useState<ChessGameState>({
    fen: game.fen(),
    moveHistory: [],
    currentMoveIndex: -1,
    isGameOver: false,
    turn: 'w',
  });

  const updateGameState = useCallback(() => {
    setGameState({
      fen: game.fen(),
      moveHistory: game.history(),
      currentMoveIndex: game.history().length - 1,
      isGameOver: game.isGameOver(),
      turn: game.turn(),
    });
  }, [game]);

  const makeMove = useCallback(
    (from: string, to: string, promotion?: string): boolean => {
      try {
        const move = game.move({
          from,
          to,
          promotion: promotion || 'q',
        });

        if (move) {
          updateGameState();
          return true;
        }
        return false;
      } catch {
        return false;
      }
    },
    [game, updateGameState]
  );

  const undoMove = useCallback(() => {
    const move = game.undo();
    if (move) {
      updateGameState();
      return true;
    }
    return false;
  }, [game, updateGameState]);

  const resetGame = useCallback(() => {
    game.reset();
    updateGameState();
  }, [game, updateGameState]);

  const loadFen = useCallback(
    (fen: string): boolean => {
      try {
        game.load(fen);
        updateGameState();
        return true;
      } catch {
        return false;
      }
    },
    [game, updateGameState]
  );

  const loadPgn = useCallback(
    (pgn: string): boolean => {
      try {
        game.loadPgn(pgn);
        updateGameState();
        return true;
      } catch {
        return false;
      }
    },
    [game, updateGameState]
  );

  const gotoMove = useCallback(
    (index: number) => {
      if (index < -1 || index >= gameState.moveHistory.length) {
        return;
      }

      // Reset game and replay moves up to index
      game.reset();
      const moves = gameState.moveHistory.slice(0, index + 1);
      moves.forEach((move) => {
        game.move(move);
      });

      setGameState({
        fen: game.fen(),
        moveHistory: gameState.moveHistory,
        currentMoveIndex: index,
        isGameOver: game.isGameOver(),
        turn: game.turn(),
      });
    },
    [game, gameState.moveHistory]
  );

  const isLegalMove = useCallback(
    (from: string, to: string): boolean => {
      const moves = game.moves({ verbose: true });
      return moves.some((move) => move.from === from && move.to === to);
    },
    [game]
  );

  const getPgn = useCallback((): string => {
    return game.pgn();
  }, [game]);

  return {
    gameState,
    makeMove,
    undoMove,
    resetGame,
    loadFen,
    loadPgn,
    gotoMove,
    isLegalMove,
    getPgn,
  };
};
