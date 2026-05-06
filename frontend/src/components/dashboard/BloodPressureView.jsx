import React from 'react';
import { useOutletContext } from 'react-router-dom';
import MainChart from '../charts/MainChart'; 
import AIInsightPanel from './AIInsightPanel';

export default function BloodPressureView() {
  const { data, latestVital } = useOutletContext();
  const vitals = latestVital || (data.length > 0 ? data[data.length - 1] : { blood_pressure_systolic: 0, blood_pressure_diastolic: 0 });

  return (
    <div className="flex flex-col gap-6 h-full">
      <div className="mb-4">
        <h2 className="text-[36px] font-serif text-[#1e1a17] tracking-tight mb-2">Blood Pressure Telemetry</h2>
        <p className="text-[#645c55] text-[15px]">Detailed historical and live view for Systolic and Diastolic pressure.</p>
      </div>

      <div className="grid grid-cols-2 gap-6">
        <div className="bg-white rounded-[20px] p-8 shadow-[0_2px_14px_-6px_rgba(0,0,0,0.06)] flex items-center justify-between">
          <div>
            <p className="text-[12px] font-bold text-[#b4a896] uppercase tracking-widest mb-1">Systolic Pressure</p>
            <div className="flex items-baseline gap-2">
              <span className="text-[48px] font-bold text-[#1a1715] tracking-tight">{Math.round(vitals.blood_pressure_systolic)}</span>
              <span className="text-[14px] font-bold text-[#b4a896] uppercase tracking-widest">mmHg</span>
            </div>
          </div>
          <div className="text-right">
            <p className="text-[12px] font-bold text-[#b4a896] uppercase tracking-widest mb-1">Normal Range</p>
            <span className="text-[18px] font-semibold text-[#645c55]">90 - 120 mmHg</span>
          </div>
        </div>
        
        <div className="bg-white rounded-[20px] p-8 shadow-[0_2px_14px_-6px_rgba(0,0,0,0.06)] flex items-center justify-between">
          <div>
            <p className="text-[12px] font-bold text-[#b4a896] uppercase tracking-widest mb-1">Diastolic Pressure</p>
            <div className="flex items-baseline gap-2">
              <span className="text-[48px] font-bold text-[#1a1715] tracking-tight">{Math.round(vitals.blood_pressure_diastolic)}</span>
              <span className="text-[14px] font-bold text-[#b4a896] uppercase tracking-widest">mmHg</span>
            </div>
          </div>
          <div className="text-right">
            <p className="text-[12px] font-bold text-[#b4a896] uppercase tracking-widest mb-1">Normal Range</p>
            <span className="text-[18px] font-semibold text-[#645c55]">60 - 80 mmHg</span>
          </div>
        </div>
      </div>

      <div className="flex gap-6 flex-1 min-h-[400px]">
        <div className="bg-white rounded-[24px] p-8 shadow-[0_2px_14px_-6px_rgba(0,0,0,0.06)] flex-[2] flex flex-col">
          <h3 className="font-serif text-[#1e1a17] text-[19px] mb-6">Live Graph</h3>
          <div className="flex-1 w-full relative">
            <MainChart data={data} filter="bp" />
          </div>
        </div>

        <div className="flex-[1]">
          <AIInsightPanel metric="bp" />
        </div>
      </div>
    </div>
  );
}
