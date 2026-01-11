import { useState, useEffect } from 'react';

const LLMSettings = () => {
  const [provider, setProvider] = useState('anthropic');
  const [apiKey, setApiKey] = useState('');
  const [model, setModel] = useState('claude-3-5-sonnet-20241022');

  useEffect(() => {
    // Load from localStorage
    const savedProvider = localStorage.getItem('llm_provider');
    const savedApiKey = localStorage.getItem('llm_api_key');
    const savedModel = localStorage.getItem('llm_model');

    if (savedProvider) setProvider(savedProvider);
    if (savedApiKey) setApiKey(savedApiKey);
    if (savedModel) setModel(savedModel);
  }, []);

  const handleSave = () => {
    localStorage.setItem('llm_provider', provider);
    localStorage.setItem('llm_api_key', apiKey);
    localStorage.setItem('llm_model', model);
    alert('LLM settings saved successfully!');
  };

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-xl font-bold text-text-primary mb-2">LLM Configuration</h3>
        <p className="text-text-secondary text-sm">
          Configure your AI model for chess coaching and analysis
        </p>
      </div>

      <div className="space-y-4">
        {/* Provider */}
        <div>
          <label className="block text-text-secondary text-sm font-medium mb-2">
            Provider
          </label>
          <select
            value={provider}
            onChange={(e) => setProvider(e.target.value)}
            className="w-full bg-surface text-text-primary px-4 py-2 rounded-lg border border-surface-dark focus:border-accent-blue focus:outline-none"
          >
            <option value="anthropic">Anthropic (Claude)</option>
            <option value="openai">OpenAI (GPT)</option>
          </select>
        </div>

        {/* API Key */}
        <div>
          <label className="block text-text-secondary text-sm font-medium mb-2">
            API Key
          </label>
          <input
            type="password"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            placeholder="Enter your API key"
            className="w-full bg-surface text-text-primary px-4 py-2 rounded-lg border border-surface-dark focus:border-accent-blue focus:outline-none"
          />
          <p className="text-text-muted text-xs mt-1">
            Your API key is stored locally in your browser
          </p>
        </div>

        {/* Model */}
        <div>
          <label className="block text-text-secondary text-sm font-medium mb-2">
            Model
          </label>
          <select
            value={model}
            onChange={(e) => setModel(e.target.value)}
            className="w-full bg-surface text-text-primary px-4 py-2 rounded-lg border border-surface-dark focus:border-accent-blue focus:outline-none"
          >
            {provider === 'anthropic' ? (
              <>
                <option value="claude-3-5-sonnet-20241022">Claude 3.5 Sonnet</option>
                <option value="claude-3-opus-20240229">Claude 3 Opus</option>
                <option value="claude-3-sonnet-20240229">Claude 3 Sonnet</option>
              </>
            ) : (
              <>
                <option value="gpt-4-turbo">GPT-4 Turbo</option>
                <option value="gpt-4">GPT-4</option>
                <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
              </>
            )}
          </select>
        </div>

        {/* Save Button */}
        <button
          onClick={handleSave}
          className="w-full px-4 py-2 bg-accent-green hover:bg-green-600 text-white rounded-lg font-medium transition-colors"
        >
          Save LLM Settings
        </button>
      </div>
    </div>
  );
};

export default LLMSettings;
