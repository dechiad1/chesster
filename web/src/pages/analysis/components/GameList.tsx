import { useState, useEffect } from 'react';
import { apiClient } from '@/api/client';
import { GameData } from '@/types';

interface GameListProps {
  onGameSelect: (game: GameData) => void;
  selectedGameId?: number;
}

const GameList = ({ onGameSelect, selectedGameId }: GameListProps) => {
  const [games, setGames] = useState<GameData[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    const fetchGames = async () => {
      try {
        setLoading(true);
        const fetchedGames = await apiClient.getGames();
        setGames(fetchedGames);
      } catch (error) {
        console.error('Error fetching games:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchGames();
  }, []);

  const filteredGames = games.filter((game) => {
    const searchLower = searchTerm.toLowerCase();
    return (
      game.game_id.toString().includes(searchLower) ||
      game.result?.toLowerCase().includes(searchLower) ||
      game.source?.toLowerCase().includes(searchLower)
    );
  });

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  if (loading) {
    return (
      <div className="bg-primary-dark rounded-lg p-6 border border-primary-light">
        <div className="text-text-secondary">Loading games...</div>
      </div>
    );
  }

  return (
    <div className="bg-primary-dark rounded-lg border border-primary-light flex flex-col h-full">
      <div className="p-4 border-b border-primary-light">
        <h3 className="text-lg font-bold text-text-primary mb-3">Game History</h3>
        <input
          type="text"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          placeholder="Search games..."
          className="w-full bg-surface text-text-primary px-4 py-2 rounded-lg border border-surface-dark focus:border-accent-blue focus:outline-none text-sm"
        />
      </div>

      <div className="flex-1 overflow-y-auto p-4">
        {filteredGames.length === 0 ? (
          <p className="text-text-secondary text-center py-8">
            {searchTerm ? 'No games found' : 'No games available'}
          </p>
        ) : (
          <div className="space-y-2">
            {filteredGames.map((game) => (
              <button
                key={game.game_id}
                onClick={() => onGameSelect(game)}
                className={`w-full text-left p-3 rounded-lg transition-colors ${
                  selectedGameId === game.game_id
                    ? 'bg-accent-blue text-white'
                    : 'bg-surface hover:bg-surface-dark text-text-primary'
                }`}
              >
                <div className="font-medium">Game #{game.game_id}</div>
                <div className="text-sm opacity-80 flex items-center justify-between mt-1">
                  <span>{game.result || 'No result'}</span>
                  <span className="text-xs">{formatDate(game.created_at)}</span>
                </div>
                {game.source && (
                  <div className="text-xs opacity-70 mt-1">
                    Source: {game.source}
                  </div>
                )}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default GameList;
