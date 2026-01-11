import { useState } from 'react';
import { useGameState } from './useGameState';
import ChessBoard from './components/ChessBoard';
import GameControls from './components/GameControls';
import MoveHistory from './components/MoveHistory';
import CoachChat from './components/CoachChat';
import ExplorationControls from './components/ExplorationControls';

const GamePage = () => {
  const {
    chessGame,
    exploration,
    handleExplore,
    handleExplorationNext,
    handleExplorationPrevious,
    handleExitExploration,
  } = useGameState();

  const [boardOrientation, setBoardOrientation] = useState<'white' | 'black'>('white');

  const { gameState, makeMove, undoMove, resetGame, gotoMove } = chessGame;
  const { explorationState } = exploration;

  const handleMove = (from: string, to: string): boolean => {
    if (explorationState.isActive) return false;
    return makeMove(from, to);
  };

  const handleNewGame = () => {
    if (explorationState.isActive) {
      alert('Please exit exploration mode first');
      return;
    }

    if (gameState.moveHistory.length > 0) {
      if (window.confirm('Start a new game? Current game will be lost.')) {
        resetGame();
      }
    } else {
      resetGame();
    }
  };

  const handleUndo = () => {
    if (explorationState.isActive) return;
    undoMove();
  };

  const handleFlip = () => {
    setBoardOrientation((prev) => (prev === 'white' ? 'black' : 'white'));
  };

  const handleResign = () => {
    if (explorationState.isActive) {
      alert('Please exit exploration mode first');
      return;
    }

    if (window.confirm('Are you sure you want to resign?')) {
      alert('Game resigned');
    }
  };

  const handleMoveClick = (index: number) => {
    if (explorationState.isActive) return;
    gotoMove(index);
  };

  return (
    <div className="p-8 max-w-7xl mx-auto">
      <h1 className="text-3xl font-bold text-text-primary mb-6">Chess Game</h1>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Board Section */}
        <div className="lg:col-span-2 space-y-4">
          <ChessBoard
            position={gameState.fen}
            onMove={handleMove}
            boardOrientation={boardOrientation}
            disabled={explorationState.isActive}
          />

          {explorationState.isActive ? (
            <ExplorationControls
              currentPosition={explorationState.currentPosition}
              totalPositions={explorationState.currentLine?.moves.length || 0}
              onPrevious={handleExplorationPrevious}
              onNext={handleExplorationNext}
              onExit={handleExitExploration}
              canGoPrevious={explorationState.currentPosition > 0}
              canGoNext={
                explorationState.currentPosition <
                (explorationState.currentLine?.moves.length || 0) - 1
              }
            />
          ) : (
            <GameControls
              onNewGame={handleNewGame}
              onUndo={handleUndo}
              onFlip={handleFlip}
              onResign={handleResign}
              canUndo={gameState.currentMoveIndex >= 0}
            />
          )}

          {/* Game Status */}
          {gameState.isGameOver && !explorationState.isActive && (
            <div className="bg-accent-red text-white rounded-lg p-4 font-medium">
              Game Over
            </div>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-4">
          <MoveHistory
            moves={gameState.moveHistory}
            currentMoveIndex={gameState.currentMoveIndex}
            onMoveClick={handleMoveClick}
          />

          {/* Turn Indicator */}
          {!explorationState.isActive && (
            <div className="bg-primary-dark rounded-lg p-4 border border-primary-light">
              <div className="text-text-secondary text-sm mb-1">Turn</div>
              <div className="text-text-primary font-medium">
                {gameState.turn === 'w' ? 'White' : 'Black'} to move
              </div>
            </div>
          )}

          {/* Coach Chat */}
          <CoachChat
            fen={gameState.fen}
            moveHistory={gameState.moveHistory}
            onExplore={handleExplore}
            disabled={explorationState.isActive}
          />
        </div>
      </div>
    </div>
  );
};

export default GamePage;
