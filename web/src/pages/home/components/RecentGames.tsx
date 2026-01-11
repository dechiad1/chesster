import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiClient } from '@/api/client';
import { GameData } from '@/types';

const RecentGames = () => {
  const [games, setGames] = useState<GameData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchGames = async () => {
      try {
        setLoading(true);
        const fetchedGames = await apiClient.getGames(undefined, 0, 5);
        setGames(fetchedGames);
        setError(null);
      } catch (err) {
        setError('Failed to load recent games');
        console.error('Error fetching games:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchGames();
  }, []);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  if (loading) {
    return (
      <div className="bg-primary-dark rounded-lg p-6 shadow-lg border border-primary-light">
        <h3 className="text-xl font-bold text-text-primary mb-4">Recent Games</h3>
        <div className="text-text-secondary">Loading games...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-primary-dark rounded-lg p-6 shadow-lg border border-primary-light">
        <h3 className="text-xl font-bold text-text-primary mb-4">Recent Games</h3>
        <div className="text-accent-red">{error}</div>
      </div>
    );
  }

  return (
    <div className="bg-primary-dark rounded-lg p-6 shadow-lg border border-primary-light">
      <h3 className="text-xl font-bold text-text-primary mb-4">Recent Games</h3>
      {games.length === 0 ? (
        <p className="text-text-secondary">No games yet. Start playing!</p>
      ) : (
        <div className="space-y-3">
          {games.map((game) => (
            <div
              key={game.game_id}
              onClick={() => navigate(`/analysis?game=${game.game_id}`)}
              className="bg-surface rounded-lg p-4 cursor-pointer hover:bg-surface-dark transition-colors"
            >
              <div className="flex justify-between items-center">
                <div className="flex-1">
                  <div className="text-text-primary font-medium">
                    Game #{game.game_id}
                  </div>
                  <div className="text-text-secondary text-sm">
                    {game.result || 'In progress'} • {game.source || 'Unknown source'}
                  </div>
                </div>
                <div className="text-text-muted text-sm">
                  {formatDate(game.created_at)}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
      {games.length > 0 && (
        <button
          onClick={() => navigate('/analysis')}
          className="mt-4 text-accent-blue hover:underline text-sm w-full text-center"
        >
          View all games →
        </button>
      )}
    </div>
  );
};

export default RecentGames;
