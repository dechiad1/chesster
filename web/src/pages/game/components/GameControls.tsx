interface GameControlsProps {
  onNewGame: () => void;
  onUndo: () => void;
  onFlip: () => void;
  onResign: () => void;
  canUndo: boolean;
}

const GameControls = ({
  onNewGame,
  onUndo,
  onFlip,
  onResign,
  canUndo,
}: GameControlsProps) => {
  return (
    <div className="flex gap-3 flex-wrap">
      <button
        onClick={onNewGame}
        className="px-4 py-2 bg-accent-green hover:bg-green-600 text-white rounded-lg font-medium transition-colors"
      >
        New Game
      </button>
      <button
        onClick={onUndo}
        disabled={!canUndo}
        className={`px-4 py-2 rounded-lg font-medium transition-colors ${
          canUndo
            ? 'bg-accent-blue hover:bg-blue-600 text-white'
            : 'bg-surface-dark text-text-muted cursor-not-allowed'
        }`}
      >
        Undo
      </button>
      <button
        onClick={onFlip}
        className="px-4 py-2 bg-surface hover:bg-surface-dark text-text-primary rounded-lg font-medium transition-colors"
      >
        Flip Board
      </button>
      <button
        onClick={onResign}
        className="px-4 py-2 bg-accent-red hover:bg-red-600 text-white rounded-lg font-medium transition-colors"
      >
        Resign
      </button>
    </div>
  );
};

export default GameControls;
