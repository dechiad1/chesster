import { useState } from 'react';
import { GameData } from '@/types';
import GameList from './components/GameList';
import GameViewer from './components/GameViewer';
import AnalysisPanel from './components/AnalysisPanel';

const AnalysisPage = () => {
  const [selectedGame, setSelectedGame] = useState<GameData | null>(null);

  return (
    <div className="p-8 max-w-7xl mx-auto">
      <h1 className="text-3xl font-bold text-text-primary mb-6">Game Analysis</h1>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[calc(100vh-180px)]">
        {/* Game List */}
        <div className="lg:col-span-1">
          <GameList
            onGameSelect={setSelectedGame}
            selectedGameId={selectedGame?.game_id}
          />
        </div>

        {/* Game Viewer */}
        <div className="lg:col-span-1">
          <GameViewer game={selectedGame} />
        </div>

        {/* Analysis Panel */}
        <div className="lg:col-span-1">
          <AnalysisPanel game={selectedGame} />
        </div>
      </div>
    </div>
  );
};

export default AnalysisPage;
