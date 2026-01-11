import { useState } from 'react';
import { apiClient } from '@/api/client';
import { GameData, GameAnalysis } from '@/types';

interface AnalysisPanelProps {
  game: GameData | null;
}

const AnalysisPanel = ({ game }: AnalysisPanelProps) => {
  const [analysis, setAnalysis] = useState<GameAnalysis | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async () => {
    if (!game) return;

    setLoading(true);
    setError(null);
    setAnalysis(null);

    try {
      const provider = localStorage.getItem('llm_provider') || 'anthropic';
      const apiKey = localStorage.getItem('llm_api_key') || '';

      if (!apiKey) {
        setError('Please configure your LLM API key in Settings first.');
        return;
      }

      const result = await apiClient.analyzeGame(
        game.game_id,
        game.pgn_data,
        provider,
        apiKey
      );
      setAnalysis(result);
    } catch (err) {
      console.error('Analysis error:', err);
      setError('Failed to analyze game. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (!game) {
    return (
      <div className="bg-primary-dark rounded-lg p-6 border border-primary-light">
        <h3 className="text-lg font-bold text-text-primary mb-3">Analysis</h3>
        <p className="text-text-secondary">Select a game to analyze</p>
      </div>
    );
  }

  return (
    <div className="bg-primary-dark rounded-lg p-6 border border-primary-light">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-bold text-text-primary">LLM Analysis</h3>
        <button
          onClick={handleAnalyze}
          disabled={loading}
          className="px-4 py-2 bg-accent-blue hover:bg-blue-600 text-white rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? 'Analyzing...' : 'Analyze Game'}
        </button>
      </div>

      {error && (
        <div className="bg-accent-red/20 text-accent-red border border-accent-red rounded-lg p-3 mb-4">
          {error}
        </div>
      )}

      {loading && (
        <div className="text-text-secondary">
          Analyzing game with LLM... This may take a minute.
        </div>
      )}

      {analysis && (
        <div className="space-y-4">
          {/* Overall Assessment */}
          <div>
            <h4 className="text-text-primary font-semibold mb-2">Overall Assessment</h4>
            <p className="text-text-secondary text-sm">{analysis.overall_assessment}</p>
          </div>

          {/* Phase Assessments */}
          <div>
            <h4 className="text-text-primary font-semibold mb-2">Opening</h4>
            <p className="text-text-secondary text-sm">{analysis.opening_assessment}</p>
          </div>

          <div>
            <h4 className="text-text-primary font-semibold mb-2">Middlegame</h4>
            <p className="text-text-secondary text-sm">{analysis.middlegame_assessment}</p>
          </div>

          <div>
            <h4 className="text-text-primary font-semibold mb-2">Endgame</h4>
            <p className="text-text-secondary text-sm">{analysis.endgame_assessment}</p>
          </div>

          {/* Critical Moments */}
          {analysis.critical_moments && analysis.critical_moments.length > 0 && (
            <div>
              <h4 className="text-text-primary font-semibold mb-2">
                Critical Moments ({analysis.critical_moments.length})
              </h4>
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {analysis.critical_moments.map((moment, index) => (
                  <div key={index} className="bg-surface rounded p-3 text-sm">
                    <div className="text-accent-blue font-medium mb-1">
                      Move {moment.move_number}
                    </div>
                    <div className="text-text-secondary mb-1">
                      Played: <span className="font-mono">{moment.played_move}</span> →{' '}
                      Best: <span className="font-mono">{moment.best_move}</span>
                    </div>
                    <div className="text-text-muted text-xs">{moment.comment}</div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {!analysis && !loading && !error && (
        <p className="text-text-secondary text-sm">
          Click "Analyze Game" to get detailed insights powered by AI
        </p>
      )}
    </div>
  );
};

export default AnalysisPanel;
