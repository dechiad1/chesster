import { useCallback } from 'react';
import { Chess } from 'chess.js';
import { useChessGame } from '@/hooks/useChessGame';
import { useExploration } from '@/hooks/useExploration';
import { ChessLine } from '@/types';

export const useGameState = () => {
  const chessGame = useChessGame();
  const exploration = useExploration();

  const handleExplore = useCallback(
    (line: ChessLine) => {
      // Save current game state
      exploration.enterExploration(
        line,
        chessGame.gameState.fen,
        chessGame.gameState.currentMoveIndex,
        chessGame.gameState.moveHistory
      );

      // Load the line for exploration
      // Start from current position and play the line moves
      const tempGame = new Chess(chessGame.gameState.fen);
      line.moves.forEach((moveUci) => {
        try {
          const from = moveUci.substring(0, 2);
          const to = moveUci.substring(2, 4);
          const promotion = moveUci.length > 4 ? moveUci[4] : undefined;
          tempGame.move({ from, to, promotion });
        } catch (e) {
          console.error('Failed to make move:', moveUci, e);
        }
      });

      // Load the final position
      chessGame.loadFen(tempGame.fen());
    },
    [chessGame, exploration]
  );

  const handleExplorationNext = useCallback(() => {
    if (!exploration.explorationState.currentLine) return;

    const nextPos = exploration.explorationState.currentPosition + 1;
    if (nextPos >= exploration.explorationState.currentLine.moves.length) return;

    exploration.nextPosition();

    // Replay moves up to next position
    const line = exploration.explorationState.currentLine;
    const tempGame = new Chess(exploration.explorationState.savedFen);

    for (let i = 0; i <= nextPos; i++) {
      const moveUci = line.moves[i];
      const from = moveUci.substring(0, 2);
      const to = moveUci.substring(2, 4);
      const promotion = moveUci.length > 4 ? moveUci[4] : undefined;
      try {
        tempGame.move({ from, to, promotion });
      } catch (e) {
        console.error('Failed to make move:', moveUci, e);
      }
    }

    chessGame.loadFen(tempGame.fen());
  }, [chessGame, exploration]);

  const handleExplorationPrevious = useCallback(() => {
    if (!exploration.explorationState.currentLine) return;
    if (exploration.explorationState.currentPosition <= 0) return;

    const prevPos = exploration.explorationState.currentPosition - 1;
    exploration.previousPosition();

    // Replay moves up to previous position
    const line = exploration.explorationState.currentLine;
    const tempGame = new Chess(exploration.explorationState.savedFen);

    for (let i = 0; i <= prevPos; i++) {
      const moveUci = line.moves[i];
      const from = moveUci.substring(0, 2);
      const to = moveUci.substring(2, 4);
      const promotion = moveUci.length > 4 ? moveUci[4] : undefined;
      try {
        tempGame.move({ from, to, promotion });
      } catch (e) {
        console.error('Failed to make move:', moveUci, e);
      }
    }

    chessGame.loadFen(tempGame.fen());
  }, [chessGame, exploration]);

  const handleExitExploration = useCallback(() => {
    const saved = exploration.exitExploration();

    // Restore saved game state
    chessGame.loadFen(saved.fen);
    // Restore move history by going to the saved move index
    chessGame.gotoMove(saved.moveIndex);
  }, [chessGame, exploration]);

  return {
    chessGame,
    exploration,
    handleExplore,
    handleExplorationNext,
    handleExplorationPrevious,
    handleExitExploration,
  };
};
