import { Link, useLocation } from 'react-router-dom';

const Sidebar = () => {
  const location = useLocation();

  const menuItems = [
    { path: '/', label: 'Home', icon: '🏠' },
    { path: '/game', label: 'Game', icon: '♟️' },
    { path: '/analysis', label: 'Analysis', icon: '📊' },
    { path: '/settings', label: 'Settings', icon: '⚙️' },
  ];

  const isActive = (path: string) => {
    if (path === '/') {
      return location.pathname === '/';
    }
    return location.pathname.startsWith(path);
  };

  return (
    <div className="w-64 bg-primary h-screen flex flex-col">
      {/* Logo/Title */}
      <div className="p-6 border-b border-primary-dark">
        <h1 className="text-2xl font-bold text-text-primary">Chess Platform</h1>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4">
        <ul className="space-y-2">
          {menuItems.map((item) => (
            <li key={item.path}>
              <Link
                to={item.path}
                className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                  isActive(item.path)
                    ? 'bg-accent-blue text-white'
                    : 'text-text-secondary hover:bg-primary-dark hover:text-text-primary'
                }`}
              >
                <span className="text-xl">{item.icon}</span>
                <span className="font-medium">{item.label}</span>
              </Link>
            </li>
          ))}
        </ul>
      </nav>

      {/* Status/Footer */}
      <div className="p-4 border-t border-primary-dark">
        <div className="text-xs text-text-muted">
          <p>Chess Platform v0.1.0</p>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
