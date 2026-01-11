import { useNavigate } from 'react-router-dom';

const QuickActions = () => {
  const navigate = useNavigate();

  const actions = [
    {
      title: 'New Game',
      description: 'Start a new chess game',
      icon: '♟️',
      color: 'bg-accent-green',
      hoverColor: 'hover:bg-green-600',
      action: () => navigate('/game'),
    },
    {
      title: 'Analyze Games',
      description: 'Review your Chess.com games',
      icon: '📊',
      color: 'bg-accent-blue',
      hoverColor: 'hover:bg-blue-600',
      action: () => navigate('/analysis'),
    },
    {
      title: 'Settings',
      description: 'Configure your preferences',
      icon: '⚙️',
      color: 'bg-surface',
      hoverColor: 'hover:bg-surface-dark',
      action: () => navigate('/settings'),
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      {actions.map((action, index) => (
        <button
          key={index}
          onClick={action.action}
          className={`${action.color} ${action.hoverColor} rounded-lg p-6 text-left transition-all transform hover:scale-105 shadow-lg`}
        >
          <div className="text-4xl mb-3">{action.icon}</div>
          <h3 className="text-xl font-bold text-text-primary mb-2">
            {action.title}
          </h3>
          <p className="text-text-secondary">{action.description}</p>
        </button>
      ))}
    </div>
  );
};

export default QuickActions;
