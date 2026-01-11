import { useState } from 'react';
import LLMSettings from './components/LLMSettings';
import ChessComSettings from './components/ChessComSettings';
import AccountForm from './components/AccountForm';

type Tab = 'llm' | 'chesscom' | 'account';

const SettingsPage = () => {
  const [activeTab, setActiveTab] = useState<Tab>('llm');

  const tabs: Array<{ id: Tab; label: string; icon: string }> = [
    { id: 'llm', label: 'LLM Config', icon: '🤖' },
    { id: 'chesscom', label: 'Chess.com', icon: '♟️' },
    { id: 'account', label: 'Account', icon: '👤' },
  ];

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold text-text-primary mb-6">Settings</h1>

      {/* Tabs */}
      <div className="flex gap-2 mb-6 border-b border-primary-light">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center gap-2 px-6 py-3 font-medium transition-all ${
              activeTab === tab.id
                ? 'text-accent-blue border-b-2 border-accent-blue'
                : 'text-text-secondary hover:text-text-primary'
            }`}
          >
            <span>{tab.icon}</span>
            <span>{tab.label}</span>
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="bg-primary-dark rounded-lg p-6 border border-primary-light">
        {activeTab === 'llm' && <LLMSettings />}
        {activeTab === 'chesscom' && <ChessComSettings />}
        {activeTab === 'account' && <AccountForm />}
      </div>
    </div>
  );
};

export default SettingsPage;
