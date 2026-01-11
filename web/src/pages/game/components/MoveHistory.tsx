interface MoveHistoryProps {
  moves: string[];
  currentMoveIndex: number;
  onMoveClick: (index: number) => void;
}

const MoveHistory = ({ moves, currentMoveIndex, onMoveClick }: MoveHistoryProps) => {
  // Group moves into pairs (white, black)
  const movePairs: Array<{ moveNumber: number; white: string; black?: string }> = [];
  for (let i = 0; i < moves.length; i += 2) {
    movePairs.push({
      moveNumber: Math.floor(i / 2) + 1,
      white: moves[i],
      black: moves[i + 1],
    });
  }

  return (
    <div className="bg-primary-dark rounded-lg p-4 border border-primary-light">
      <h3 className="text-lg font-bold text-text-primary mb-3">Move History</h3>
      <div className="max-h-96 overflow-y-auto">
        {movePairs.length === 0 ? (
          <p className="text-text-secondary text-sm">No moves yet</p>
        ) : (
          <div className="space-y-1">
            {movePairs.map((pair, pairIndex) => (
              <div
                key={pairIndex}
                className="grid grid-cols-[40px_1fr_1fr] gap-2 text-sm"
              >
                <span className="text-text-muted">{pair.moveNumber}.</span>
                <button
                  onClick={() => onMoveClick(pairIndex * 2)}
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
                    onClick={() => onMoveClick(pairIndex * 2 + 1)}
                    className={`text-left px-2 py-1 rounded transition-colors ${
                      currentMoveIndex === pairIndex * 2 + 1
                        ? 'bg-accent-blue text-white'
                        : 'text-text-primary hover:bg-surface'
                    }`}
                  >
                    {pair.black}
                  </button>
                ) : (
                  <span></span>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default MoveHistory;
