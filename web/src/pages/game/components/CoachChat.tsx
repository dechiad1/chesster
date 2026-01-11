import { useState, useRef, useEffect } from 'react';
import { apiClient } from '@/api/client';
import { CoachResponse, ChessLine } from '@/types';
import LinesSuggestion from './LinesSuggestion';

interface Message {
  role: 'user' | 'coach';
  content: string;
  lines?: ChessLine[];
}

interface CoachChatProps {
  fen: string;
  moveHistory: string[];
  onExplore: (line: ChessLine) => void;
  disabled?: boolean;
}

const CoachChat = ({ fen, moveHistory, onExplore, disabled = false }: CoachChatProps) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput('');

    // Add user message
    setMessages((prev) => [...prev, { role: 'user', content: userMessage }]);
    setLoading(true);

    try {
      // Get API key and provider from localStorage (set in Settings)
      const provider = localStorage.getItem('llm_provider') || 'anthropic';
      const apiKey = localStorage.getItem('llm_api_key') || '';

      if (!apiKey) {
        setMessages((prev) => [
          ...prev,
          {
            role: 'coach',
            content: 'Please configure your LLM API key in Settings first.',
          },
        ]);
        return;
      }

      const response: CoachResponse = await apiClient.coachChat(
        userMessage,
        fen,
        moveHistory,
        provider,
        apiKey
      );

      // Add coach response
      if (response.response_type === 'lines' && response.lines) {
        setMessages((prev) => [
          ...prev,
          {
            role: 'coach',
            content: response.content,
            lines: response.lines,
          },
        ]);
      } else {
        setMessages((prev) => [
          ...prev,
          {
            role: 'coach',
            content: response.content,
          },
        ]);
      }
    } catch (error) {
      console.error('Coach chat error:', error);
      setMessages((prev) => [
        ...prev,
        {
          role: 'coach',
          content: 'Sorry, I encountered an error. Please try again.',
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="bg-primary-dark rounded-lg border border-primary-light flex flex-col h-[500px]">
      <div className="p-4 border-b border-primary-light">
        <h3 className="text-lg font-bold text-text-primary">Chess Coach</h3>
        <p className="text-text-muted text-xs">Ask me anything about the position</p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.length === 0 && (
          <div className="text-text-secondary text-center py-8">
            <p>👋 Hello! I'm your chess coach.</p>
            <p className="text-sm mt-2">Ask me for move suggestions, analysis, or typical continuations.</p>
          </div>
        )}

        {messages.map((message, index) => (
          <div key={index}>
            {message.role === 'user' ? (
              <div className="bg-surface rounded-lg p-3 border-l-4 border-accent-blue">
                <div className="text-accent-blue font-bold text-sm mb-1">YOU</div>
                <div className="text-text-primary">{message.content}</div>
              </div>
            ) : message.lines ? (
              <LinesSuggestion
                content={message.content}
                lines={message.lines}
                onExplore={onExplore}
              />
            ) : (
              <div className="bg-primary-dark rounded-lg p-3 border-l-4 border-accent-green">
                <div className="text-accent-green font-bold text-sm mb-1">COACH</div>
                <div className="text-text-primary whitespace-pre-wrap">{message.content}</div>
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="bg-primary-dark rounded-lg p-3 border-l-4 border-accent-green">
            <div className="text-accent-green font-bold text-sm mb-1">COACH</div>
            <div className="text-text-secondary">Thinking...</div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t border-primary-light">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={disabled || loading}
            placeholder={disabled ? 'Exit exploration mode first' : 'Ask the coach...'}
            className="flex-1 bg-surface text-text-primary px-4 py-2 rounded-lg border border-surface-dark focus:border-accent-blue focus:outline-none disabled:opacity-50 disabled:cursor-not-allowed"
          />
          <button
            onClick={handleSend}
            disabled={disabled || loading || !input.trim()}
            className="px-6 py-2 bg-accent-blue hover:bg-blue-600 text-white rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
};

export default CoachChat;
