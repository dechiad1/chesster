import WelcomeCard from './components/WelcomeCard';
import QuickActions from './components/QuickActions';
import RecentGames from './components/RecentGames';

const HomePage = () => {
  return (
    <div className="p-8 max-w-7xl mx-auto">
      <div className="space-y-8">
        {/* Welcome Section */}
        <WelcomeCard />

        {/* Quick Actions */}
        <QuickActions />

        {/* Recent Games */}
        <RecentGames />
      </div>
    </div>
  );
};

export default HomePage;
