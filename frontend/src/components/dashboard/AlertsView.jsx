import React from 'react';
import AlertPanel from './AlertPanel';

export default function AlertsView() {
  return (
    <div className="flex flex-col gap-6 h-full">
      <div className="mb-4">
        <h2 className="text-[36px] font-serif text-[#1e1a17] tracking-tight mb-2">System Alerts</h2>
        <p className="text-[#645c55] text-[15px]">Historical and active system notifications regarding patient status.</p>
      </div>

      <div className="flex-1 w-full max-w-4xl max-h-[800px]">
        {/* We reuse AlertPanel but in a larger context */}
        <AlertPanel />
      </div>
    </div>
  );
}
