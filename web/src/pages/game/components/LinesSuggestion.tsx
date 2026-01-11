import { ChessLine } from '@/types';
import LineCard from './LineCard';

interface LinesSuggestionProps {
  content: string;
  lines: ChessLine[];
  onExplore: (line: ChessLine) => void;
}

const LinesSuggestion = ({ content, lines, onExplore }: LinesSuggestionProps) => {
  return (
    <div className="bg-primary-dark rounded-lg p-4 border-l-4 border-accent-green">
      <div className="flex items-start gap-2 mb-3">
        <span className="text-accent-green font-bold text-sm">COACH</span>
      </div>
      <div className="text-text-primary mb-4">{content}</div>
      <div className="space-y-3">
        {lines.map((line, index) => (
          <LineCard key={index} line={line} onExplore={onExplore} />
        ))}
      </div>
    </div>
  );
};

export default LinesSuggestion;
