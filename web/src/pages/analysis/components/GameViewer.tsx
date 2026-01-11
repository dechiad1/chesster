import { useState, useEffect } from 'react';
import { Chess } from 'chess.js';
import { Chessboard } from 'react-chessboard';
import { GameData } from '@/types';

interface GameViewerProps {
  game: GameData | null;
}

const GameViewer = ({ game }: GameViewerProps) => {
  const [chess] = useState(() => new Chess());
  const [fen, setFen] = useState(chess.fen());
  const [moveHistory, setMoveHistory] = useState<string[]>([]);
  const [currentMoveIndex, setCurrentMoveIndex] = useState(-1);

  useEffect(() => {
    if (!game) {
      chess.reset();
      setFen(chess.fen());
      setMoveHistory([]);
      setCurrentMoveIndex(-1);
      return;
    }

    try {
      chess.loadPgn(game.pgn_data);
      const history = chess.history();
      setMoveHistory(history);
      setCurrentMoveIndex(history.length - 1);
      setFen(chess.fen());
    } catch (error) {
      console.error('Error loading PGN:', error);
    }
  }, [game, chess]);

  const gotoMove = (index: number) => {
    chess.reset();
    const moves = moveHistory.slice(0, index + 1);
    moves.forEach((move) => {
      chess.move(move);
    });
    setFen(chess.fen());
    setCurrentMoveIndex(index);
  };

  const handlePrevious = () => {
    if (currentMoveIndex > -1) {
      gotoMove(currentMoveIndex - 1);
    }
  };

  const handleNext = () => {
    if (currentMoveIndex < moveHistory.length - 1) {
      gotoMove(currentMoveIndex + 1);
    }
  };

  const handleFirst = () => {
    gotoMove(-1);
  };

  const handleLast = () => {
    gotoMove(moveHistory.length - 1);
  };

  if (!game) {
    return (
      <div className="bg-primary-dark rounded-lg p-6 border border-primary-light h-full flex items-center justify-center">
        <p className="text-text-secondary">Select a game to view</p>
      </div>
    );
  }

  // Group moves into pairs
  const movePairs: Array<{ moveNumber: number; white: string; black?: string }> = [];
  for (let i = 0; i < moveHistory.length; i += 2) {
    movePairs.push({
      moveNumber: Math.floor(i / 2) + 1,
      white: moveHistory[i],
      black: moveHistory[i + 1],
    });
  }

  return (
    <div className="space-y-4">
      {/* Board */}
      <div className="bg-primary-dark rounded-lg p-6 border border-primary-light">
        <div className="max-w-2xl mx-auto">
          <Chessboard
            position={fen}
            customBoardStyle={{
              borderRadius: '8px',
              boxShadow: '0 4px 6px rgba(0, 0, 0, 0.3)',
            }}
            customDarkSquareStyle={{ backgroundColor: '#779952' }}
            customLightSquareStyle={{ backgroundColor: '#edeed1' }}
            arePiecesDraggable={false}
          />
        </div>

        {/* Navigation Controls */}
        <div className="flex gap-2 mt-4 justify-center">
          <button
            onClick={handleFirst}
            disabled={currentMoveIndex === -1}
            className="px-4 py-2 bg-surface hover:bg-surface-dark text-text-primary rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            ⏮ First
          </button>
          <button
            onClick={handlePrevious}
            disabled={currentMoveIndex === -1}
            className="px-4 py-2 bg-surface hover:bg-surface-dark text-text-primary rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            ← Previous
          </button>
          <button
            onClick={handleNext}
            disabled={currentMoveIndex >= moveHistory.length - 1}
            className="px-4 py-2 bg-surface hover:bg-surface-dark text-text-primary rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Next →
          </button>
          <button
            onClick={handleLast}
            disabled={currentMoveIndex >= moveHistory.length - 1}
            className="px-4 py-2 bg-surface hover:bg-surface-dark text-text-primary rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Last ⏭
          </button>
        </div>
      </div>

      {/* Move History */}
      <div className="bg-primary-dark rounded-lg p-4 border border-primary-light">
        <h3 className="text-lg font-bold text-text-primary mb-3">Moves</h3>
        <div className="max-h-48 overflow-y-auto">
          {movePairs.length === 0 ? (
            <p className="text-text-secondary text-sm">No moves</p>
          ) : (
            <div className="grid grid-cols-[40px_1fr_1fr] gap-2 text-sm">
              {movePairs.map((pair, pairIndex) => (
                <>
                  <span key={`num-${pairIndex}`} className="text-text-muted">
                    {pair.moveNumber}.
                  </span>
                  <button
                    key={`white-${pairIndex}`}
                    onClick={() => gotoMove(pairIndex * 2)}
                    className={`text-left px-2 py-1 rounded transition-colors ${
                      currentMoveIndex === pairIndex * 2
                        ? 'bg-accent-blue text-white'
                        : 'text-text-primary hover:bg-surface'
                    }`}
                  >
                    {pair.white}
                  </button>
                  {pair.black ? (
                    <button
                      key={`black-${pairIndex}`}
                      onClick={() => gotoMove(pairIndex * 2 + 1)}
                      className={`text-left px-2 py-1 rounded transition-colors ${
                        currentMoveIndex === pairIndex * 2 + 1
                          ? 'bg-accent-blue text-white'
                          : 'text-text-primary hover:bg-surface'
                      }`}
                    >
                      {pair.black}
                    </button>
                  ) : (
                    <span key={`empty-${pairIndex}`}></span>
                  )}
                </>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default GameViewer;
