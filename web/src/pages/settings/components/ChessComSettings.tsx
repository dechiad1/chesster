import { useState } from 'react';
import { apiClient } from '@/api/client';

const ChessComSettings = () => {
  const [username, setUsername] = useState('');
  const [gameCount, setGameCount] = useState(15);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const handleFetchGames = async () => {
    if (!username.trim()) {
      setMessage({ type: 'error', text: 'Please enter a username' });
      return;
    }

    setLoading(true);
    setMessage(null);

    try {
      const games = await apiClient.fetchChessComGames(username, gameCount);
      setMessage({
        type: 'success',
        text: `Successfully fetched ${games.length} games from Chess.com`,
      });
    } catch (error) {
      setMessage({
        type: 'error',
        text: 'Failed to fetch games. Please check the username and try again.',
      });
      console.error('Error fetching Chess.com games:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-xl font-bold text-text-primary mb-2">Chess.com Integration</h3>
        <p className="text-text-secondary text-sm">
          Import and analyze your games from Chess.com
        </p>
      </div>

      <div className="space-y-4">
        {/* Username */}
        <div>
          <label className="block text-text-secondary text-sm font-medium mb-2">
            Chess.com Username
          </label>
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="Enter your Chess.com username"
            className="w-full bg-surface text-text-primary px-4 py-2 rounded-lg border border-surface-dark focus:border-accent-blue focus:outline-none"
          />
        </div>

        {/* Game Count */}
        <div>
          <label className="block text-text-secondary text-sm font-medium mb-2">
            Number of Games to Fetch
          </label>
          <input
            type="number"
            value={gameCount}
            onChange={(e) => setGameCount(parseInt(e.target.value) || 15)}
            min="1"
            max="50"
            className="w-full bg-surface text-text-primary px-4 py-2 rounded-lg border border-surface-dark focus:border-accent-blue focus:outline-none"
          />
          <p className="text-text-muted text-xs mt-1">
            Maximum 50 games
          </p>
        </div>

        {/* Fetch Button */}
        <button
          onClick={handleFetchGames}
          disabled={loading}
          className="w-full px-4 py-2 bg-accent-blue hover:bg-blue-600 text-white rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? 'Fetching Games...' : 'Fetch Games from Chess.com'}
        </button>

        {/* Message */}
        {message && (
          <div
            className={`p-3 rounded-lg ${
              message.type === 'success'
                ? 'bg-accent-green/20 text-accent-green border border-accent-green'
                : 'bg-accent-red/20 text-accent-red border border-accent-red'
            }`}
          >
            {message.text}
          </div>
        )}
      </div>

      <div className="border-t border-primary-light pt-4">
        <p className="text-text-muted text-sm">
          <strong>Note:</strong> Fetched games will be stored in the database and
          available in the Analysis page for review and coaching insights.
        </p>
      </div>
    </div>
  );
};

export default ChessComSettings;
