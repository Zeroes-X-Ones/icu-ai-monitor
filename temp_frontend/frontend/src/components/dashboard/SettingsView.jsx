import React from 'react';

export default function SettingsView() {
  return (
    <div className="flex flex-col gap-6 h-full">
      <div className="mb-4">
        <h2 className="text-[36px] font-serif text-[#1e1a17] tracking-tight mb-2">System Settings</h2>
        <p className="text-[#645c55] text-[15px]">Configure dashboard preferences and application settings.</p>
      </div>

      <div className="bg-white rounded-[24px] p-8 shadow-[0_2px_14px_-6px_rgba(0,0,0,0.06)] flex-1 min-h-[400px] flex flex-col justify-center items-center">
        <p className="text-[#8c8273] text-lg font-medium">Settings panel is currently under construction.</p>
      </div>
    </div>
  );
}
