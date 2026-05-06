// import React from 'react';
// import { NavLink } from 'react-router-dom';
// import { LayoutDashboard, Heart, Wind, Droplets, Bell, Settings, LogOut, Terminal, Clock } from 'lucide-react';

// export default function Sidebar() {
//   const navLinkClasses = ({ isActive }) =>
//     `flex items-center gap-3 px-8 py-3 mr-6 font-medium text-[13px] transition-colors ${
//       isActive
//         ? 'bg-[#f5f2eb] text-[#1e1b1a] rounded-r-xl shadow-sm'
//         : 'hover:bg-white/5 rounded-r-xl text-[#a69f95]'
//     }`;

//   return (
//     <aside className="w-60 bg-[#1e1b1a] flex flex-col text-[#a69f95] z-20 shrink-0">
//       <div className="p-8 pb-4 mb-4">
//         <h1 className="font-serif text-[#eae5de] text-[26px] tracking-wide leading-tight mb-1">
//           VitalsAI<span className="text-[#a69f95]">.</span>
//         </h1>
//         <p className="text-[8px] uppercase tracking-[0.2em] text-[#867b71] font-semibold mt-2">
//           Intensive Intelligence
//         </p>
//       </div>

//       <nav className="flex-1 space-y-2 px-0 mt-4">
//         <NavLink to="/" end className={navLinkClasses}>
//           <LayoutDashboard size={16} />
//           Dashboard
//         </NavLink>
//         <NavLink to="/heart-rate" className={navLinkClasses}>
//           <Heart size={16} />
//           Heart Rate
//         </NavLink>
//         <NavLink to="/spo2" className={navLinkClasses}>
//           <Wind size={16} />
//           SpO₂ Level
//         </NavLink>
//         <NavLink to="/blood-pressure" className={navLinkClasses}>
//           <Droplets size={16} />
//           Blood Pressure
//         </NavLink>
//         <NavLink to="/alerts" className={navLinkClasses}>
//           <Bell size={16} />
//           Alerts
//         </NavLink>
//         <NavLink to="/history" className={navLinkClasses}>
//           <Clock size={16} />
//           History
//         </NavLink>
//         <NavLink to="/settings" className={navLinkClasses}>
//           <Settings size={16} />
//           Settings
//         </NavLink>
//       </nav>

//       <div className="p-8 border-t border-white/5 flex flex-col gap-4">
//         <button className="flex items-center gap-3 text-[13px] font-medium hover:text-white transition-colors">
//           <div className="w-5 h-5 rounded-full bg-white/10 flex items-center justify-center text-[10px] font-bold">?</div>
//           Terminal
//         </button>
//         <div className="mt-4 pt-4 border-t border-white/5">
//           <button className="flex items-center gap-3 text-[13px] font-medium hover:text-white transition-colors">
//             <LogOut size={16} />
//             Sign out
//           </button>
//         </div>
//       </div>
//     </aside>
//   );
// }

import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Heart, Wind, Droplets, Bell, Settings, LogOut, Terminal, Clock } from 'lucide-react';

export default function Sidebar() {
  return (
    <aside style={{
      width: 220,
      background: '#ffffff',
      borderRight: '1px solid #f1f5f9',
      display: 'flex',
      flexDirection: 'column',
      flexShrink: 0,
      zIndex: 20,
      fontFamily: "'Inter', -apple-system, sans-serif",
    }}>

      {/* Logo */}
      <div style={{ padding: '24px 20px 20px', borderBottom: '1px solid #f1f5f9' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 6 }}>
          <div style={{
            width: 32, height: 32, borderRadius: 9,
            background: 'linear-gradient(135deg, #3b82f6, #6366f1)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: 14, color: '#ffffff', fontWeight: 800,
            flexShrink: 0,
          }}>
            ✦
          </div>
          <div>
            <h1 style={{ fontSize: 15, fontWeight: 800, color: '#0f172a', margin: 0, letterSpacing: -0.3 }}>
              ICU Monitor
            </h1>
            <p style={{ fontSize: 9, fontWeight: 600, color: '#94a3b8', margin: 0, letterSpacing: 1.5, textTransform: 'uppercase' }}>
              Clinical Suite
            </p>
          </div>
        </div>
      </div>

      {/* Nav sections */}
      <nav style={{ flex: 1, padding: '16px 12px', display: 'flex', flexDirection: 'column', gap: 2 }}>

        <p style={{ fontSize: 9, fontWeight: 700, color: '#cbd5e1', letterSpacing: 2, textTransform: 'uppercase', margin: '0 0 8px 8px' }}>
          Monitoring
        </p>

        <SidebarLink to="/" end icon={<LayoutDashboard size={15} />} label="Overview" />
        <SidebarLink to="/heart-rate" icon={<Heart size={15} />} label="Heart Rate" />
        <SidebarLink to="/spo2" icon={<Wind size={15} />} label="Oxygen (SpO₂)" />
        <SidebarLink to="/blood-pressure" icon={<Droplets size={15} />} label="Blood Pressure" />

        <p style={{ fontSize: 9, fontWeight: 700, color: '#cbd5e1', letterSpacing: 2, textTransform: 'uppercase', margin: '16px 0 8px 8px' }}>
          Workflow
        </p>

        <SidebarLink to="/alerts" icon={<Bell size={15} />} label="Alerts" />
        <SidebarLink to="/history" icon={<Clock size={15} />} label="History" />
        <SidebarLink to="/settings" icon={<Settings size={15} />} label="Settings" />

      </nav>

      {/* Footer */}
      <div style={{ padding: '16px 12px', borderTop: '1px solid #f1f5f9' }}>

        {/* Disclaimer */}
        <div style={{
          background: '#f8fafc', borderRadius: 10, padding: '10px 12px',
          border: '1px solid #f1f5f9', marginBottom: 12,
        }}>
          <p style={{ fontSize: 9, fontWeight: 700, color: '#94a3b8', textTransform: 'uppercase', letterSpacing: 1.5, margin: '0 0 3px' }}>
            Disclaimer
          </p>
          <p style={{ fontSize: 10, color: '#94a3b8', margin: 0, lineHeight: 1.5 }}>
            For demonstration only. Not for clinical use.
          </p>
        </div>

        <button style={{
          display: 'flex', alignItems: 'center', gap: 8,
          width: '100%', padding: '8px 10px', borderRadius: 8,
          border: 'none', background: 'transparent', cursor: 'pointer',
          fontSize: 12, fontWeight: 500, color: '#94a3b8',
          fontFamily: 'inherit', transition: 'all 0.15s',
        }}
          onMouseEnter={e => { e.currentTarget.style.background = '#f8fafc'; e.currentTarget.style.color = '#ef4444'; }}
          onMouseLeave={e => { e.currentTarget.style.background = 'transparent'; e.currentTarget.style.color = '#94a3b8'; }}
        >
          <LogOut size={13} />
          Sign out
        </button>
      </div>

    </aside>
  );
}

function SidebarLink({ to, end, icon, label }) {
  return (
    <NavLink
      to={to}
      end={end}
      style={({ isActive }) => ({
        display: 'flex',
        alignItems: 'center',
        gap: 10,
        padding: '8px 10px',
        borderRadius: 9,
        fontSize: 13,
        fontWeight: isActive ? 600 : 500,
        color: isActive ? '#0f172a' : '#64748b',
        background: isActive ? '#f1f5f9' : 'transparent',
        textDecoration: 'none',
        transition: 'all 0.15s',
        position: 'relative',
      })}
      onMouseEnter={e => {
        if (!e.currentTarget.getAttribute('aria-current')) {
          e.currentTarget.style.background = '#f8fafc';
          e.currentTarget.style.color = '#0f172a';
        }
      }}
      onMouseLeave={e => {
        if (!e.currentTarget.getAttribute('aria-current')) {
          e.currentTarget.style.background = 'transparent';
          e.currentTarget.style.color = '#64748b';
        }
      }}
    >
      {({ isActive }) => (
        <>
          <span style={{ color: isActive ? '#3b82f6' : '#94a3b8', display: 'flex', alignItems: 'center' }}>
            {icon}
          </span>
          {label}
          {isActive && (
            <span style={{
              marginLeft: 'auto', width: 4, height: 4, borderRadius: '50%',
              background: '#3b82f6', flexShrink: 0,
            }} />
          )}
        </>
      )}
    </NavLink>
  );
}