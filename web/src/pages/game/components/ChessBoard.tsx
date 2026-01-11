import { Chessboard } from 'react-chessboard';
import { Square } from 'chess.js';

interface ChessBoardProps {
  position: string;
  onMove: (from: string, to: string) => boolean;
  boardOrientation?: 'white' | 'black';
  disabled?: boolean;
}

const ChessBoard = ({
  position,
  onMove,
  boardOrientation = 'white',
  disabled = false,
}: ChessBoardProps) => {
  const onDrop = (sourceSquare: Square, targetSquare: Square): boolean => {
    if (disabled) return false;
    return onMove(sourceSquare, targetSquare);
  };

  return (
    <div className="w-full max-w-2xl">
      <Chessboard
        position={position}
        onPieceDrop={onDrop}
        boardOrientation={boardOrientation}
        customBoardStyle={{
          borderRadius: '8px',
          boxShadow: '0 4px 6px rgba(0, 0, 0, 0.3)',
        }}
        customDarkSquareStyle={{ backgroundColor: '#779952' }}
        customLightSquareStyle={{ backgroundColor: '#edeed1' }}
      />
    </div>
  );
};

export default ChessBoard;
