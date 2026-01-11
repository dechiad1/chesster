import { ChessLine } from '@/types';

interface LineCardProps {
  line: ChessLine;
  onExplore: (line: ChessLine) => void;
}

const LineCard = ({ line, onExplore }: LineCardProps) => {
  const formatMoves = (movesSan: string[]): string => {
    const pairs: string[] = [];
    for (let i = 0; i < movesSan.length; i += 2) {
      const moveNumber = Math.floor(i / 2) + 1;
      const whitMove = movesSan[i];
      const blackMove = movesSan[i + 1];
      pairs.push(`${moveNumber}. ${whiteMove}${blackMove ? ` ${blackMove}` : ''}`);
    }
    return pairs.join(' ');
  };

  return (
    <button
      onClick={() => onExplore(line)}
      className="w-full bg-surface rounded-lg p-4 text-left border-2 border-transparent hover:border-accent-blue transition-all cursor-pointer"
    >
      <div className="font-bold text-text-primary mb-2">{line.description}</div>
      <div className="text-text-secondary text-sm font-mono">
        {formatMoves(line.moves_san)}
      </div>
      {line.evaluation !== undefined && (
        <div className="text-text-muted text-xs mt-2">
          Eval: {line.evaluation > 0 ? '+' : ''}
          {(line.evaluation / 100).toFixed(2)}
        </div>
      )}
    </button>
  );
};

export default LineCard;
