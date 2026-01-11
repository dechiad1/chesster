const WelcomeCard = () => {
  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 18) return 'Good afternoon';
    return 'Good evening';
  };

  return (
    <div className="bg-primary-dark rounded-lg p-8 shadow-lg border border-primary-light">
      <h2 className="text-3xl font-bold text-text-primary mb-2">
        {getGreeting()}!
      </h2>
      <p className="text-text-secondary text-lg">
        Welcome to your chess training platform. Ready to improve your game?
      </p>
    </div>
  );
};

export default WelcomeCard;
