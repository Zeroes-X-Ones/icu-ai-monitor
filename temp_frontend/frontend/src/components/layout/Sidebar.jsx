import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Heart, Wind, Droplets, Bell, Settings, LogOut, Terminal, Clock } from 'lucide-react';

export default function Sidebar() {
  const navLinkClasses = ({ isActive }) =>
    `flex items-center gap-3 px-8 py-3 mr-6 font-medium text-[13px] transition-colors ${
      isActive
        ? 'bg-[#f5f2eb] text-[#1e1b1a] rounded-r-xl shadow-sm'
        : 'hover:bg-white/5 rounded-r-xl text-[#a69f95]'
    }`;

  return (
    <aside className="w-60 bg-[#1e1b1a] flex flex-col text-[#a69f95] z-20 shrink-0">
      <div className="p-8 pb-4 mb-4">
        <h1 className="font-serif text-[#eae5de] text-[26px] tracking-wide leading-tight mb-1">
          VitalsAI<span className="text-[#a69f95]">.</span>
        </h1>
        <p className="text-[8px] uppercase tracking-[0.2em] text-[#867b71] font-semibold mt-2">
          Intensive Intelligence
        </p>
      </div>

      <nav className="flex-1 space-y-2 px-0 mt-4">
        <NavLink to="/" end className={navLinkClasses}>
          <LayoutDashboard size={16} />
          Dashboard
        </NavLink>
        <NavLink to="/heart-rate" className={navLinkClasses}>
          <Heart size={16} />
          Heart Rate
        </NavLink>
        <NavLink to="/spo2" className={navLinkClasses}>
          <Wind size={16} />
          SpO₂ Level
        </NavLink>
        <NavLink to="/blood-pressure" className={navLinkClasses}>
          <Droplets size={16} />
          Blood Pressure
        </NavLink>
        <NavLink to="/alerts" className={navLinkClasses}>
          <Bell size={16} />
          Alerts
        </NavLink>
        <NavLink to="/history" className={navLinkClasses}>
          <Clock size={16} />
          History
        </NavLink>
        <NavLink to="/settings" className={navLinkClasses}>
          <Settings size={16} />
          Settings
        </NavLink>
      </nav>

      <div className="p-8 border-t border-white/5 flex flex-col gap-4">
        <button className="flex items-center gap-3 text-[13px] font-medium hover:text-white transition-colors">
          <div className="w-5 h-5 rounded-full bg-white/10 flex items-center justify-center text-[10px] font-bold">?</div>
          Terminal
        </button>
        <div className="mt-4 pt-4 border-t border-white/5">
          <button className="flex items-center gap-3 text-[13px] font-medium hover:text-white transition-colors">
            <LogOut size={16} />
            Sign out
          </button>
        </div>
      </div>
    </aside>
  );
}
