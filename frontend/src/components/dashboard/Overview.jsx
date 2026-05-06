// import React from 'react';
// import { useOutletContext } from 'react-router-dom';
// import MainChart from '../charts/MainChart';
// import AlertPanel from './AlertPanel';
// import AIInsightPanel from './AIInsightPanel';
// import IntelligencePanel from './IntelligencePanel';

// export default function Overview() {
//   const { data, isConnected, latestVital } = useOutletContext();

//   const vitals = latestVital || (data.length > 0 ? data[data.length - 1] : { heart_rate: 0, spo2: 0, blood_pressure_systolic: 0, blood_pressure_diastolic: 0, alert_level: 'INFO' });

//   return (
//     <>
//       <div className="mb-10">
//         <h2 className="text-[42px] font-serif text-[#1e1a17] tracking-tight mb-2">Good morning, Dr. Reynolds .</h2>
//         <p className="text-[#645c55] text-[15px]">Here is your live patient telemetry overview.</p>
//       </div>

//       {/* TOP ROW: Pill-shaped KPI Cards (6 wide) */}
//       <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-6 gap-5 mb-6">
//         <div className="bg-white rounded-[20px] p-6 shadow-[0_2px_14px_-6px_rgba(0,0,0,0.06)] h-32 flex flex-col justify-between">
//           <p className="text-[10px] font-bold text-[#b4a896] uppercase tracking-widest">Heart Rate</p>
//           <div className="flex items-baseline gap-1.5 border-b border-[#f0ece5] pb-2 inline-block max-w-max">
//             <span className="text-[28px] font-bold text-[#1a1715] tracking-tight">{Math.round(vitals.heart_rate)}</span>
//           </div>
//           <p className="text-[9px] font-bold text-[#b4a896] uppercase tracking-widest mt-auto">BPM</p>
//         </div>

//         <div className="bg-white rounded-[20px] p-6 shadow-[0_2px_14px_-6px_rgba(0,0,0,0.06)] h-32 flex flex-col justify-between">
//           <p className="text-[10px] font-bold text-[#b4a896] uppercase tracking-widest">SpO2 Level</p>
//           <div className="flex items-baseline gap-1.5 border-b border-[#f0ece5] pb-2 inline-block max-w-max">
//             <span className="text-[28px] font-bold text-[#1a1715] tracking-tight">{Math.round(vitals.spo2)}</span>
//           </div>
//           <p className="text-[9px] font-bold text-[#b4a896] uppercase tracking-widest mt-auto">%</p>
//         </div>

//         <div className="bg-white rounded-[20px] p-6 shadow-[0_2px_14px_-6px_rgba(0,0,0,0.06)] h-32 flex flex-col justify-between">
//           <p className="text-[10px] font-bold text-[#b4a896] uppercase tracking-widest">BP Systolic</p>
//           <div className="flex items-baseline gap-1.5 border-b border-[#f0ece5] pb-2 inline-block max-w-max">
//             <span className="text-[28px] font-bold text-[#1a1715] tracking-tight">{Math.round(vitals.blood_pressure_systolic)}</span>
//           </div>
//           <p className="text-[9px] font-bold text-[#b4a896] uppercase tracking-widest mt-auto">mmHg</p>
//         </div>

//         <div className="bg-white rounded-[20px] p-6 shadow-[0_2px_14px_-6px_rgba(0,0,0,0.06)] h-32 flex flex-col justify-between">
//           <p className="text-[10px] font-bold text-[#b4a896] uppercase tracking-widest">BP Diastolic</p>
//           <div className="flex items-baseline gap-1.5 border-b border-[#f0ece5] pb-2 inline-block max-w-max">
//             <span className="text-[28px] font-bold text-[#1a1715] tracking-tight">{Math.round(vitals.blood_pressure_diastolic)}</span>
//           </div>
//           <p className="text-[9px] font-bold text-[#b4a896] uppercase tracking-widest mt-auto">mmHg</p>
//         </div>

//         <div className="bg-white rounded-[20px] p-6 shadow-[0_2px_14px_-6px_rgba(0,0,0,0.06)] h-32 flex flex-col justify-between">
//           <p className="text-[10px] font-bold text-[#b4a896] uppercase tracking-widest">Vitals Status</p>
//           <div className="flex items-baseline gap-1.5 border-b border-[#f0ece5] pb-2 inline-block max-w-max">
//             <span className={`text-[13px] font-bold tracking-wide uppercase ${vitals.alert_level === 'CRITICAL' ? 'text-[#e13f28]' : vitals.alert_level === 'WARNING' ? 'text-[#e0912f]' : 'text-[#2a874b]'}`}>{vitals.alert_level || 'INFO'}</span>
//           </div>
//           <p className="text-[9px] font-bold text-[#b4a896] uppercase tracking-widest mt-auto">Active State</p>
//         </div>

//         <div className="bg-white rounded-[20px] p-6 shadow-[0_2px_14px_-6px_rgba(0,0,0,0.06)] h-32 flex flex-col justify-between">
//           <p className="text-[10px] font-bold text-[#b4a896] uppercase tracking-widest">Connection</p>
//           <div className="flex items-baseline gap-2 border-b border-[#f0ece5] pb-2 inline-flex items-center max-w-max">
//             <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-[#2a874b]' : 'bg-[#e13f28]'}`}></div>
//             <span className="text-[13px] font-bold text-[#1a1715] uppercase tracking-wide">{isConnected ? 'Live' : 'Offline'}</span>
//           </div>
//           <p className="text-[9px] font-bold text-[#b4a896] uppercase tracking-widest mt-auto">Socket</p>
//         </div>

//       </div>

//       {/* MIDDLE ROW: AI Insights and Notifications */}
//       <div className="flex flex-col xl:flex-row gap-5 mb-5 w-full">
//         <div className="flex-[3]">
//           <AIInsightPanel />
//         </div>
//         <div className="flex-[2] xl:w-5/12">
//           <AlertPanel />
//         </div>
//       </div>

//       {/* INTELLIGENCE ROW: Event Detection, Recommendations, Timeline */}
//       <div className="mb-5 w-full">
//         <IntelligencePanel />
//       </div>

//       {/* BOTTOM ROW: Real-time Graph Card */}
//       <div className="bg-white rounded-[24px] p-8 shadow-[0_2px_14px_-6px_rgba(0,0,0,0.06)] w-full h-[450px] flex flex-col">
//         <div className="flex items-center gap-1 mb-8">
//           <h3 className="font-serif text-[#1e1a17] text-[19px]">Telemetry Source</h3>
//         </div>
//         <div className="flex-1 w-full relative">
//           <MainChart data={data} />
//         </div>
//       </div>

//       {/* BOTTOM ACTIONS PILLS */}
//       <div className="flex items-center gap-4 mt-8">
//         <button className="bg-[#b46b41] hover:bg-[#a35e36] text-white px-6 py-2.5 rounded-full font-medium text-xs tracking-wide shadow-sm transition-colors">
//           Open Patient Board
//         </button>
//         <button className="bg-white hover:bg-slate-50 text-[#1a1715] px-6 py-2.5 rounded-full font-medium text-xs tracking-wide shadow-[0_2px_8px_-4px_rgba(0,0,0,0.1)] transition-colors border border-transparent">
//           View AI History
//         </button>
//         <button className="bg-white hover:bg-slate-50 text-[#1a1715] px-6 py-2.5 rounded-full font-medium text-xs tracking-wide shadow-[0_2px_8px_-4px_rgba(0,0,0,0.1)] transition-colors border border-transparent">
//           Settings
//         </button>
//       </div>
//     </>
//   );
// }




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
    <div style={{ background: '#f0f2f5', minHeight: '100vh', fontFamily: "'Inter', -apple-system, sans-serif" }}>

      {/* Patient Header Bar */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '10px 28px',
        background: '#ffffff',
        borderBottom: '1px solid #e8edf2',
        position: 'sticky',
        top: 0,
        zIndex: 10,
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <span style={{ fontSize: 10, color: '#94a3b8', fontWeight: 600, letterSpacing: 1.5, textTransform: 'uppercase' }}>Active Patient</span>
          <span style={{ color: '#cbd5e1' }}>·</span>
          <span style={{ fontSize: 13, color: '#1e293b', fontWeight: 700 }}>Patient #2841</span>
          <span style={{ color: '#cbd5e1' }}>·</span>
          <span style={{ fontSize: 12, color: '#64748b' }}>BED-04 · ICU Ward A</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <span style={{
            display: 'flex', alignItems: 'center', gap: 5,
            background: '#f0fdf4', border: '1px solid #bbf7d0',
            borderRadius: 20, padding: '3px 10px',
            fontSize: 10, fontWeight: 700, color: '#16a34a', letterSpacing: 1.5, textTransform: 'uppercase'
          }}>
            <span style={{ width: 6, height: 6, borderRadius: '50%', background: '#22c55e', display: 'inline-block' }} />
            Low Risk
          </span>
          <span style={{
            display: 'flex', alignItems: 'center', gap: 5,
            background: isConnected ? '#f0fdf4' : '#fef2f2',
            border: `1px solid ${isConnected ? '#bbf7d0' : '#fecaca'}`,
            borderRadius: 20, padding: '3px 10px',
            fontSize: 10, fontWeight: 700,
            color: isConnected ? '#16a34a' : '#dc2626',
            letterSpacing: 1.5, textTransform: 'uppercase'
          }}>
            <span style={{
              width: 6, height: 6, borderRadius: '50%',
              background: isConnected ? '#22c55e' : '#ef4444',
              display: 'inline-block',
            }} />
            {isConnected ? 'Live' : 'Offline'}
          </span>
          <span style={{ fontSize: 12, color: '#94a3b8', fontWeight: 500 }}>
            {new Date().toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
          </span>
        </div>
      </div>

      <div style={{ padding: '28px' }}>

        {/* Page Title */}
        <div style={{ marginBottom: 24 }}>
          <h2 style={{ fontSize: 26, fontWeight: 700, color: '#0f172a', margin: 0, letterSpacing: -0.5 }}>
            Good morning, Dr. Reynolds.
          </h2>
          <p style={{ fontSize: 13, color: '#64748b', marginTop: 4, margin: '4px 0 0' }}>
            Here is your live patient telemetry overview.
          </p>
        </div>

        {/* TOP ROW: 4 Vital Cards matching screenshot */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16, marginBottom: 16 }}>

          <VitalKpiCard
            abbr="HR"
            label="Heart Rate"
            value={Math.round(vitals.heart_rate)}
            unit="BPM"
            color="#ef4444"
            status="NORMAL"
            rangeLabel="Range 60–100 bpm"
            trendLabel="-1.5 over 30s"
            trendDown={true}
            data={data}
            field="heart_rate"
          />

          <VitalKpiCard
            abbr="SPO₂"
            label="Oxygen Saturation"
            value={vitals.spo2?.toFixed ? vitals.spo2.toFixed(1) : vitals.spo2}
            unit="%"
            color="#3b82f6"
            status="NORMAL"
            rangeLabel="Range 94–100 %"
            trendLabel="Stable"
            trendDown={false}
            data={data}
            field="spo2"
          />

          <VitalKpiCard
            abbr="RR"
            label="Respiratory Rate"
            value={16}
            unit="BR/MIN"
            color="#22c55e"
            status="NORMAL"
            rangeLabel="Range 12–22 br/min"
            trendLabel="Stable"
            trendDown={false}
            data={data}
            field="heart_rate"
          />

          <VitalKpiCard
            abbr="BP"
            label="Blood Pressure"
            value={Math.round(vitals.blood_pressure_systolic)}
            unit={`/ ${Math.round(vitals.blood_pressure_diastolic)} MMHG`}
            color="#a855f7"
            status="NORMAL"
            rangeLabel="Range 110–130 mmHg"
            trendLabel="Stable"
            trendDown={false}
            data={data}
            field="blood_pressure_systolic"
          />

        </div>

        {/* SECOND ROW: 3 Trend Charts + a status card
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 16, marginBottom: 16 }}>

          <TrendCard label="Heart Rate · trend" color="#ef4444" data={data} field="heart_rate" yMin={70} yMax={160} />
          <TrendCard label="Oxygen Saturation · trend" color="#3b82f6" data={data} field="spo2" yMin={85} yMax={100} />
          <TrendCard label="Respiratory Rate · trend" color="#22c55e" data={data} field="heart_rate" yMin={12} yMax={36} />

        </div> */}

        {/* MIDDLE ROW: AI Insights + Alerts */}
        <div style={{ display: 'flex', gap: 16, marginBottom: 16, width: '100%' }}>
          <div style={{ flex: 3, minWidth: 0 }}>
            <AIInsightPanel />
          </div>
          <div style={{ flex: 2, minWidth: 0 }}>
            <AlertPanel />
          </div>
        </div>

        {/* INTELLIGENCE ROW */}
        <div style={{ marginBottom: 16 }}>
          <IntelligencePanel />
        </div>

        {/* BOTTOM: Telemetry Chart */}
        <div style={{
          background: '#ffffff',
          borderRadius: 16,
          padding: '22px 24px',
          boxShadow: '0 1px 4px rgba(0,0,0,0.06)',
          height: 450,
          display: 'flex',
          flexDirection: 'column',
          boxSizing: 'border-box',
        }}>
          <div style={{ marginBottom: 18 }}>
            <h3 style={{ fontSize: 15, fontWeight: 700, color: '#0f172a', margin: 0 }}>Telemetry Source</h3>
          </div>
          <div style={{ flex: 1, width: '100%', position: 'relative' }}>
            <MainChart data={data} />
          </div>
        </div>

        {/* BOTTOM ACTIONS */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginTop: 20 }}>
          <button style={{
            background: '#1e293b', color: '#ffffff', border: 'none',
            padding: '9px 20px', borderRadius: 50,
            fontSize: 11, fontWeight: 600, cursor: 'pointer', fontFamily: 'inherit',
          }}>
            Open Patient Board
          </button>
          <button style={{
            background: '#ffffff', color: '#374151',
            border: '1px solid #e5e7eb',
            padding: '9px 20px', borderRadius: 50,
            fontSize: 11, fontWeight: 600, cursor: 'pointer', fontFamily: 'inherit',
            boxShadow: '0 1px 3px rgba(0,0,0,0.06)',
          }}>
            View AI History
          </button>
          <button style={{
            background: '#ffffff', color: '#374151',
            border: '1px solid #e5e7eb',
            padding: '9px 20px', borderRadius: 50,
            fontSize: 11, fontWeight: 600, cursor: 'pointer', fontFamily: 'inherit',
            boxShadow: '0 1px 3px rgba(0,0,0,0.06)',
          }}>
            Settings
          </button>
        </div>

      </div>

      <style>{`@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');`}</style>
    </div>
  );
}

/* ── Vital KPI card with inline sparkline ── */
function VitalKpiCard({ abbr, label, value, unit, color, status, rangeLabel, trendLabel, trendDown, data, field }) {
  const points = data.slice(-30).map(d => d[field] ?? 0);
  const min = Math.min(...points);
  const max = Math.max(...points);
  const span = max - min || 1;
  const W = 260, H = 56;
  const coords = points.map((v, i) => {
    const x = (i / Math.max(points.length - 1, 1)) * W;
    const y = H - ((v - min) / span) * (H - 4) - 2;
    return `${x},${y}`;
  });
  const polyline = coords.join(' ');
  const area = `M0,${H} L${coords.join(' L')} L${W},${H} Z`;

  return (
    <div style={{
      background: '#ffffff',
      borderRadius: 16,
      padding: '18px 20px 14px',
      boxShadow: '0 1px 4px rgba(0,0,0,0.07)',
      display: 'flex',
      flexDirection: 'column',
      overflow: 'hidden',
      position: 'relative',
    }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <span style={{ fontSize: 11, fontWeight: 700, color, letterSpacing: 0.5 }}>{abbr}</span>
          <span style={{ fontSize: 12, color: '#64748b', fontWeight: 500 }}>{label}</span>
        </div>
        <span style={{
          fontSize: 9, fontWeight: 700, letterSpacing: 1,
          background: '#f0fdf4', color: '#16a34a',
          border: '1px solid #bbf7d0',
          borderRadius: 20, padding: '2px 8px', textTransform: 'uppercase',
        }}>
          + {status}
        </span>
      </div>

      {/* Big value */}
      <div style={{ display: 'flex', alignItems: 'baseline', gap: 6, marginBottom: 4 }}>
        <span style={{ fontSize: 44, fontWeight: 700, color, lineHeight: 1, letterSpacing: -1 }}>{value}</span>
        <span style={{ fontSize: 13, color: '#94a3b8', fontWeight: 500 }}>{unit}</span>
      </div>

      {/* Sparkline — full-bleed */}
      {points.length > 1 && (
        <div style={{ margin: '0 -20px', height: 58 }}>
          <svg width="100%" height="58" viewBox={`0 0 ${W} ${H}`} preserveAspectRatio="none">
            <defs>
              <linearGradient id={`g-${field}-${abbr}`} x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor={color} stopOpacity="0.15" />
                <stop offset="100%" stopColor={color} stopOpacity="0" />
              </linearGradient>
            </defs>
            <path d={area} fill={`url(#g-${field}-${abbr})`} />
            <polyline points={polyline} fill="none" stroke={color} strokeWidth="1.8" strokeLinejoin="round" strokeLinecap="round" />
          </svg>
        </div>
      )}

      {/* Footer */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 6 }}>
        <span style={{ fontSize: 10, color: '#94a3b8' }}>{rangeLabel}</span>
        <span style={{ fontSize: 10, color: '#94a3b8', display: 'flex', alignItems: 'center', gap: 3 }}>
          {trendDown && <span style={{ color: '#f59e0b', fontSize: 9 }}>↓</span>}
          {trendLabel}
        </span>
      </div>
    </div>
  );
}

// function TrendCard({ label, color, data, field, yMin, yMax }) {
//   const values = data.slice(-50).map(d => d[field] ?? 0);

//   const min = Math.min(...values);
//   const max = Math.max(...values);

//   // 🚨 FIX: avoid flat data black block
//   const hasVariation = max - min > 1;

//   if (!hasVariation) {
//     return (
//       <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-sm">
//         <h4 className="text-sm font-semibold text-slate-700 mb-2">{label}</h4>
//         <p className="text-xs text-slate-400">Stable — no significant variation</p>
//       </div>
//     );
//   }

//   const W = 400, H = 100;

//   const coords = values.map((v, i) => {
//     const x = (i / (values.length - 1)) * W;
//     const y = H - ((v - min) / (max - min)) * (H - 10);
//     return `${x},${y}`;
//   });

//   const polyline = coords.join(' ');
//   const area = `M0,${H} L${coords.join(' L')} L${W},${H} Z`;

//   return (
//     <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-sm">
//       <h4 className="text-sm font-semibold text-slate-700 mb-3">{label}</h4>

//       <svg width="100%" height="100" viewBox={`0 0 ${W} ${H}`}>
//         <defs>
//           <linearGradient id={`grad-${field}`} x1="0" y1="0" x2="0" y2="1">
//             <stop offset="0%" stopColor={color} stopOpacity="0.15" />
//             <stop offset="100%" stopColor={color} stopOpacity="0" />
//           </linearGradient>
//         </defs>

//         <path d={area} fill={`url(#grad-${field})`} />
//         <polyline
//           points={polyline}
//           fill="none"
//           stroke={color}
//           strokeWidth="2"
//         />
//       </svg>
//     </div>
//   );
// }