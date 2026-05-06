import React, { useState, useEffect } from 'react';

export default function SettingsView() {
  const [theme, setTheme] = useState(localStorage.getItem('theme') || 'light');

  useEffect(() => {
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
      localStorage.setItem('theme', 'dark');
    } else {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('theme', 'light');
    }
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prev => prev === 'light' ? 'dark' : 'light');
  };
  return (
    <div className="flex flex-col gap-6 h-full">
      <div className="mb-4">
        <h2 className="text-[36px] font-serif text-[#1e1a17] tracking-tight mb-2">System Settings</h2>
        <p className="text-[#645c55] text-[15px]">Configure dashboard preferences and application settings.</p>
      </div>

      <div className="bg-white dark:bg-slate-800 rounded-[24px] p-8 shadow-[0_2px_14px_-6px_rgba(0,0,0,0.06)] flex-1 min-h-[400px] flex flex-col gap-6">
        
        {/* Working Theme Toggle */}
        <div className="flex items-center justify-between p-4 border border-slate-100 dark:border-slate-700 rounded-xl">
          <div>
            <h3 className="font-semibold text-slate-800 dark:text-slate-200">Appearance (Theme)</h3>
            <p className="text-sm text-slate-500 dark:text-slate-400">Toggle between Light and Dark mode</p>
          </div>
          <button 
            onClick={toggleTheme}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${theme === 'dark' ? 'bg-slate-100 text-slate-900' : 'bg-slate-900 text-white'}`}
          >
            {theme === 'dark' ? 'Switch to Light' : 'Switch to Dark'}
          </button>
        </div>

        {/* Coming Soon Settings */}
        <div className="flex items-center justify-between p-4 border border-slate-100 dark:border-slate-700 rounded-xl opacity-50">
          <div>
            <h3 className="font-semibold text-slate-800 dark:text-slate-200">Notification Preferences</h3>
            <p className="text-sm text-slate-500 dark:text-slate-400">Configure email and SMS alerts</p>
          </div>
          <span className="px-3 py-1 bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 rounded-full text-xs font-bold">Coming Soon</span>
        </div>

        <div className="flex items-center justify-between p-4 border border-slate-100 dark:border-slate-700 rounded-xl opacity-50">
          <div>
            <h3 className="font-semibold text-slate-800 dark:text-slate-200">Data Export Settings</h3>
            <p className="text-sm text-slate-500 dark:text-slate-400">Configure automated data backups</p>
          </div>
          <span className="px-3 py-1 bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 rounded-full text-xs font-bold">Coming Soon</span>
        </div>

      </div>
    </div>
  );
}
