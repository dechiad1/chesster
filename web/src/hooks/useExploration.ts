import { useState, useCallback } from 'react';
import { ChessLine } from '@/types';

export interface ExplorationState {
  isActive: boolean;
  currentLine: ChessLine | null;
  currentPosition: number;
  savedFen: string;
  savedMoveIndex: number;
  savedMoveHistory: string[];
}

export const useExploration = () => {
  const [explorationState, setExplorationState] = useState<ExplorationState>({
    isActive: false,
    currentLine: null,
    currentPosition: 0,
    savedFen: '',
    savedMoveIndex: -1,
    savedMoveHistory: [],
  });

  const enterExploration = useCallback(
    (line: ChessLine, currentFen: string, currentMoveIndex: number, moveHistory: string[]) => {
      setExplorationState({
        isActive: true,
        currentLine: line,
        currentPosition: 0,
        savedFen: currentFen,
        savedMoveIndex: currentMoveIndex,
        savedMoveHistory: [...moveHistory],
      });
    },
    []
  );

  const exitExploration = useCallback((): {
    fen: string;
    moveIndex: number;
    moveHistory: string[];
  } => {
    const saved = {
      fen: explorationState.savedFen,
      moveIndex: explorationState.savedMoveIndex,
      moveHistory: explorationState.savedMoveHistory,
    };

    setExplorationState({
      isActive: false,
      currentLine: null,
      currentPosition: 0,
      savedFen: '',
      savedMoveIndex: -1,
      savedMoveHistory: [],
    });

    return saved;
  }, [explorationState]);

  const nextPosition = useCallback(() => {
    setExplorationState((prev) => ({
      ...prev,
      currentPosition: Math.min(
        prev.currentPosition + 1,
        (prev.currentLine?.moves.length || 1) - 1
      ),
    }));
  }, []);

  const previousPosition = useCallback(() => {
    setExplorationState((prev) => ({
      ...prev,
      currentPosition: Math.max(prev.currentPosition - 1, 0),
    }));
  }, []);

  return {
    explorationState,
    enterExploration,
    exitExploration,
    nextPosition,
    previousPosition,
  };
};
