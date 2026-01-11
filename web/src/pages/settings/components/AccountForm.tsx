import { useState } from 'react';

const AccountForm = () => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    fullName: '',
    skillLevel: 'intermediate',
    preferredColor: 'white',
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSave = () => {
    // TODO: Save to API when user management is fully implemented
    console.log('Saving account data:', formData);
    alert('Account settings saved (local only - API integration pending)');
  };

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-xl font-bold text-text-primary mb-2">Account Settings</h3>
        <p className="text-text-secondary text-sm">
          Manage your profile information
        </p>
      </div>

      <div className="space-y-4">
        {/* Username */}
        <div>
          <label className="block text-text-secondary text-sm font-medium mb-2">
            Username
          </label>
          <input
            type="text"
            name="username"
            value={formData.username}
            onChange={handleChange}
            placeholder="Enter username"
            className="w-full bg-surface text-text-primary px-4 py-2 rounded-lg border border-surface-dark focus:border-accent-blue focus:outline-none"
          />
        </div>

        {/* Email */}
        <div>
          <label className="block text-text-secondary text-sm font-medium mb-2">
            Email
          </label>
          <input
            type="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            placeholder="Enter email"
            className="w-full bg-surface text-text-primary px-4 py-2 rounded-lg border border-surface-dark focus:border-accent-blue focus:outline-none"
          />
        </div>

        {/* Full Name */}
        <div>
          <label className="block text-text-secondary text-sm font-medium mb-2">
            Full Name
          </label>
          <input
            type="text"
            name="fullName"
            value={formData.fullName}
            onChange={handleChange}
            placeholder="Enter full name"
            className="w-full bg-surface text-text-primary px-4 py-2 rounded-lg border border-surface-dark focus:border-accent-blue focus:outline-none"
          />
        </div>

        {/* Skill Level */}
        <div>
          <label className="block text-text-secondary text-sm font-medium mb-2">
            Skill Level
          </label>
          <select
            name="skillLevel"
            value={formData.skillLevel}
            onChange={handleChange}
            className="w-full bg-surface text-text-primary px-4 py-2 rounded-lg border border-surface-dark focus:border-accent-blue focus:outline-none"
          >
            <option value="beginner">Beginner</option>
            <option value="intermediate">Intermediate</option>
            <option value="advanced">Advanced</option>
            <option value="expert">Expert</option>
          </select>
        </div>

        {/* Preferred Color */}
        <div>
          <label className="block text-text-secondary text-sm font-medium mb-2">
            Preferred Color
          </label>
          <select
            name="preferredColor"
            value={formData.preferredColor}
            onChange={handleChange}
            className="w-full bg-surface text-text-primary px-4 py-2 rounded-lg border border-surface-dark focus:border-accent-blue focus:outline-none"
          >
            <option value="white">White</option>
            <option value="black">Black</option>
            <option value="random">Random</option>
          </select>
        </div>

        {/* Save Button */}
        <button
          onClick={handleSave}
          className="w-full px-4 py-2 bg-accent-green hover:bg-green-600 text-white rounded-lg font-medium transition-colors"
        >
          Save Account Settings
        </button>
      </div>
    </div>
  );
};

export default AccountForm;
