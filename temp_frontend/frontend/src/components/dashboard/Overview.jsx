import React from 'react';
import { useOutletContext } from 'react-router-dom';
import MainChart from '../charts/MainChart';
import AlertPanel from './AlertPanel';
import AIInsightPanel from './AIInsightPanel';
import IntelligencePanel from './IntelligencePanel';

export default function Overview() {
  const { data, isConnected, latestVital } = useOutletContext();
  
  const vitals = latestVital || (data.length > 0 ? data[data.length - 1] : { heart_rate: 0, spo2: 0, blood_pressure_systolic: 0, blood_pressure_diastolic: 0, alert_level: 'INFO' });

  return (
    <>
      <div className="mb-10">
        <h2 className="text-[42px] font-serif text-[#1e1a17] tracking-tight mb-2">Good morning, Dr. Reynolds .</h2>
        <p className="text-[#645c55] text-[15px]">Here is your live patient telemetry overview.</p>
      </div>

      {/* TOP ROW: Pill-shaped KPI Cards (6 wide) */}
      <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-6 gap-5 mb-6">
        <div className="bg-white rounded-[20px] p-6 shadow-[0_2px_14px_-6px_rgba(0,0,0,0.06)] h-32 flex flex-col justify-between">
          <p className="text-[10px] font-bold text-[#b4a896] uppercase tracking-widest">Heart Rate</p>
          <div className="flex items-baseline gap-1.5 border-b border-[#f0ece5] pb-2 inline-block max-w-max">
            <span className="text-[28px] font-bold text-[#1a1715] tracking-tight">{Math.round(vitals.heart_rate)}</span>
          </div>
          <p className="text-[9px] font-bold text-[#b4a896] uppercase tracking-widest mt-auto">BPM</p>
        </div>

        <div className="bg-white rounded-[20px] p-6 shadow-[0_2px_14px_-6px_rgba(0,0,0,0.06)] h-32 flex flex-col justify-between">
          <p className="text-[10px] font-bold text-[#b4a896] uppercase tracking-widest">SpO2 Level</p>
          <div className="flex items-baseline gap-1.5 border-b border-[#f0ece5] pb-2 inline-block max-w-max">
            <span className="text-[28px] font-bold text-[#1a1715] tracking-tight">{Math.round(vitals.spo2)}</span>
          </div>
          <p className="text-[9px] font-bold text-[#b4a896] uppercase tracking-widest mt-auto">%</p>
        </div>

        <div className="bg-white rounded-[20px] p-6 shadow-[0_2px_14px_-6px_rgba(0,0,0,0.06)] h-32 flex flex-col justify-between">
          <p className="text-[10px] font-bold text-[#b4a896] uppercase tracking-widest">BP Systolic</p>
          <div className="flex items-baseline gap-1.5 border-b border-[#f0ece5] pb-2 inline-block max-w-max">
            <span className="text-[28px] font-bold text-[#1a1715] tracking-tight">{Math.round(vitals.blood_pressure_systolic)}</span>
          </div>
          <p className="text-[9px] font-bold text-[#b4a896] uppercase tracking-widest mt-auto">mmHg</p>
        </div>

        <div className="bg-white rounded-[20px] p-6 shadow-[0_2px_14px_-6px_rgba(0,0,0,0.06)] h-32 flex flex-col justify-between">
          <p className="text-[10px] font-bold text-[#b4a896] uppercase tracking-widest">BP Diastolic</p>
          <div className="flex items-baseline gap-1.5 border-b border-[#f0ece5] pb-2 inline-block max-w-max">
            <span className="text-[28px] font-bold text-[#1a1715] tracking-tight">{Math.round(vitals.blood_pressure_diastolic)}</span>
          </div>
          <p className="text-[9px] font-bold text-[#b4a896] uppercase tracking-widest mt-auto">mmHg</p>
        </div>

        <div className="bg-white rounded-[20px] p-6 shadow-[0_2px_14px_-6px_rgba(0,0,0,0.06)] h-32 flex flex-col justify-between">
          <p className="text-[10px] font-bold text-[#b4a896] uppercase tracking-widest">Vitals Status</p>
          <div className="flex items-baseline gap-1.5 border-b border-[#f0ece5] pb-2 inline-block max-w-max">
            <span className={`text-[13px] font-bold tracking-wide uppercase ${vitals.alert_level === 'CRITICAL' ? 'text-[#e13f28]' : vitals.alert_level === 'WARNING' ? 'text-[#e0912f]' : 'text-[#2a874b]'}`}>{vitals.alert_level || 'INFO'}</span>
          </div>
          <p className="text-[9px] font-bold text-[#b4a896] uppercase tracking-widest mt-auto">Active State</p>
        </div>
        
        <div className="bg-white rounded-[20px] p-6 shadow-[0_2px_14px_-6px_rgba(0,0,0,0.06)] h-32 flex flex-col justify-between">
          <p className="text-[10px] font-bold text-[#b4a896] uppercase tracking-widest">Connection</p>
          <div className="flex items-baseline gap-2 border-b border-[#f0ece5] pb-2 inline-flex items-center max-w-max">
            <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-[#2a874b]' : 'bg-[#e13f28]'}`}></div>
            <span className="text-[13px] font-bold text-[#1a1715] uppercase tracking-wide">{isConnected ? 'Live' : 'Offline'}</span>
          </div>
          <p className="text-[9px] font-bold text-[#b4a896] uppercase tracking-widest mt-auto">Socket</p>
        </div>

      </div>

      {/* MIDDLE ROW: AI Insights and Notifications */}
      <div className="flex flex-col xl:flex-row gap-5 mb-5 w-full">
        <div className="flex-[3]">
          <AIInsightPanel />
        </div>
        <div className="flex-[2] xl:w-5/12">
          <AlertPanel />
        </div>
      </div>

      {/* INTELLIGENCE ROW: Event Detection, Recommendations, Timeline */}
      <div className="mb-5 w-full">
         <IntelligencePanel />
      </div>

      {/* BOTTOM ROW: Real-time Graph Card */}
      <div className="bg-white rounded-[24px] p-8 shadow-[0_2px_14px_-6px_rgba(0,0,0,0.06)] w-full h-[450px] flex flex-col">
        <div className="flex items-center gap-1 mb-8">
          <h3 className="font-serif text-[#1e1a17] text-[19px]">Telemetry Source</h3>
        </div>
        <div className="flex-1 w-full relative">
          <MainChart data={data} />
        </div>
      </div>

      {/* BOTTOM ACTIONS PILLS */}
      <div className="flex items-center gap-4 mt-8">
        <button className="bg-[#b46b41] hover:bg-[#a35e36] text-white px-6 py-2.5 rounded-full font-medium text-xs tracking-wide shadow-sm transition-colors">
          Open Patient Board
        </button>
        <button className="bg-white hover:bg-slate-50 text-[#1a1715] px-6 py-2.5 rounded-full font-medium text-xs tracking-wide shadow-[0_2px_8px_-4px_rgba(0,0,0,0.1)] transition-colors border border-transparent">
          View AI History
        </button>
        <button className="bg-white hover:bg-slate-50 text-[#1a1715] px-6 py-2.5 rounded-full font-medium text-xs tracking-wide shadow-[0_2px_8px_-4px_rgba(0,0,0,0.1)] transition-colors border border-transparent">
          Settings
        </button>
      </div>
    </>
  );
}
