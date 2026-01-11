import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Sidebar from './components/shared/Sidebar';
import HomePage from './pages/home/HomePage';
import GamePage from './pages/game/GamePage';
import AnalysisPage from './pages/analysis/AnalysisPage';
import SettingsPage from './pages/settings/SettingsPage';

function App() {
  return (
    <Router>
      <div className="flex h-screen bg-primary">
        <Sidebar />
        <main className="flex-1 overflow-auto">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/game" element={<GamePage />} />
            <Route path="/analysis" element={<AnalysisPage />} />
            <Route path="/settings" element={<SettingsPage />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
