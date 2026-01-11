interface ExplorationControlsProps {
  currentPosition: number;
  totalPositions: number;
  onPrevious: () => void;
  onNext: () => void;
  onExit: () => void;
  canGoPrevious: boolean;
  canGoNext: boolean;
}

const ExplorationControls = ({
  currentPosition,
  totalPositions,
  onPrevious,
  onNext,
  onExit,
  canGoPrevious,
  canGoNext,
}: ExplorationControlsProps) => {
  return (
    <div className="bg-surface border-2 border-accent-blue rounded-lg p-4 shadow-lg">
      <div className="text-accent-blue font-bold mb-3 text-center">
        EXPLORING LINE
      </div>

      <div className="text-text-primary text-center mb-4">
        Position {currentPosition + 1} / {totalPositions}
      </div>

      <div className="flex gap-3">
        <button
          onClick={onPrevious}
          disabled={!canGoPrevious}
          className={`flex-1 px-4 py-2 rounded-lg font-medium transition-colors ${
            canGoPrevious
              ? 'bg-accent-blue hover:bg-blue-600 text-white'
              : 'bg-surface-dark text-text-muted cursor-not-allowed'
          }`}
        >
          ← Previous
        </button>

        <button
          onClick={onNext}
          disabled={!canGoNext}
          className={`flex-1 px-4 py-2 rounded-lg font-medium transition-colors ${
            canGoNext
              ? 'bg-accent-blue hover:bg-blue-600 text-white'
              : 'bg-surface-dark text-text-muted cursor-not-allowed'
          }`}
        >
          Next →
        </button>
      </div>

      <button
        onClick={onExit}
        className="w-full mt-3 px-4 py-2 bg-accent-red hover:bg-red-600 text-white rounded-lg font-medium transition-colors"
      >
        ← Back to Game
      </button>
    </div>
  );
};

export default ExplorationControls;
