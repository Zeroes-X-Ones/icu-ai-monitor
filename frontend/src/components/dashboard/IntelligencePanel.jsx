// import React, { useState, useEffect } from 'react';
// import { useOutletContext } from 'react-router-dom';
// import { AlertTriangle, Activity, CheckCircle2, ChevronRight, CheckSquare, Clock } from 'lucide-react';

// export default function IntelligencePanel() {
//   const { data, timeWindow, setTimeWindow, loadingHistory } = useOutletContext();
//   const [analysis, setAnalysis] = useState(null);
//   const [loading, setLoading] = useState(true);

//   useEffect(() => {
//     const fetchIntelligence = async () => {
//       setLoading(true);
//       try {
//         const res = await fetch(`http://localhost:8000/api/v1/analysis/?window=${timeWindow}`);
//         const json = await res.json();
//         setAnalysis(json);
//       } catch (err) {
//         console.error(err);
//       }
//       setLoading(false);
//     };

//     fetchIntelligence();
//     const interval = setInterval(fetchIntelligence, 30000); 
//     return () => clearInterval(interval);
//   }, [timeWindow]);

//   if ((loading || loadingHistory) && !analysis) {
//     return <div className="bg-white rounded-[24px] p-8 shadow-[0_2px_14px_-6px_rgba(0,0,0,0.06)] h-[400px] flex items-center justify-center text-slate-400">Loading Clinical Intelligence...</div>;
//   }

//   if (!analysis) return null;

//   return (
//     <div className="bg-white rounded-[24px] p-8 shadow-[0_2px_14px_-6px_rgba(0,0,0,0.06)] h-[400px] flex flex-col gap-4">

//       <div className="flex items-center justify-between mb-2">
//          <h2 className="font-serif text-[#1e1a17] text-[19px]">Clinical Intelligence & Events</h2>
//          <div className="flex gap-2 bg-slate-50 p-1 rounded-xl border border-slate-100">
//             {[15, 30, 60].map((w) => (
//               <button
//                 key={w}
//                 onClick={() => setTimeWindow(w)}
//                 className={`px-3 py-1.5 text-[11px] font-bold rounded-lg transition-colors ${timeWindow === w ? 'bg-white shadow-sm text-slate-800' : 'text-slate-500 hover:text-slate-700'}`}
//               >
//                 {w} Min
//               </button>
//             ))}
//          </div>
//       </div>

//       <div className="flex flex-1 gap-8 overflow-hidden">
//         {/* 1. Critical Events Panel */}
//         <div className="flex-1 flex flex-col min-w-0 pr-6 border-r border-slate-100 h-full">
//           <h3 className="font-serif text-[#1e1a17] text-[16px] mb-4 flex items-center gap-2">
//              <AlertTriangle size={16} className="text-[#b46b41]"/> Critical Events
//           </h3>
//         <div className="flex-1 overflow-y-auto pr-2 custom-scrollbar flex flex-col gap-3">
//           {analysis.events && analysis.events.length > 0 ? (
//             analysis.events.slice(0, 5).map((e, idx) => (
//                <div key={idx} className={`p-3 rounded-xl border ${e.severity === 'CRITICAL' ? 'bg-red-50 border-red-100' : 'bg-orange-50 border-orange-100'} flex items-start gap-3`}>
//                   <div className={`mt-0.5 w-6 h-6 rounded-full flex items-center justify-center shrink-0 ${e.severity === 'CRITICAL' ? 'bg-red-100 text-red-600' : 'bg-orange-100 text-orange-600'}`}>
//                      {e.type.includes('HR') ? <Activity size={12}/> : <AlertTriangle size={12}/>}
//                   </div>
//                   <div>
//                     <p className="text-[10px] font-bold uppercase tracking-wider text-slate-500 mb-0.5 flex items-center gap-2">
//                        {e.type.replace('_', ' ')}
//                        <span className={`px-1.5 py-0.5 rounded-sm text-[8px] ${e.severity === 'CRITICAL' ? 'bg-red-600 text-white' : 'bg-orange-500 text-white'}`}>Priority: {e.priority}</span>
//                     </p>
//                     <p className="text-[12px] font-medium text-slate-800 leading-snug">{e.description}</p>
//                     <p className="text-[10px] text-slate-400 mt-1 font-mono">{new Date(e.timestamp).toLocaleTimeString()}</p>
//                   </div>
//                </div>
//             ))
//           ) : (
//              <div className="p-4 rounded-xl border border-slate-100 bg-slate-50 flex items-center gap-3">
//                 <CheckCircle2 size={16} className="text-emerald-500"/>
//                 <p className="text-[12px] text-slate-600 font-medium">No critical events detected in the current window.</p>
//              </div>
//           )}
//         </div>
//       </div>

//         {/* 2. Recommendation Panel */}
//         <div className="flex-1 flex flex-col min-w-0 pr-6 border-r border-slate-100 h-full">
//           <h3 className="font-serif text-[#1e1a17] text-[16px] mb-4 flex items-center gap-2">
//              <CheckSquare size={16} className="text-[#b46b41]"/> Recommendations
//           </h3>
//         <div className="flex-1 overflow-y-auto pr-2 custom-scrollbar flex flex-col gap-3">
//            {analysis.recommendations && analysis.recommendations.length > 0 ? (
//              analysis.recommendations.map((r, idx) => (
//                 <div key={idx} className="p-3 rounded-xl border border-blue-100 bg-blue-50 flex items-start gap-3">
//                    <div className="mt-0.5"><ChevronRight size={16} className="text-blue-500"/></div>
//                    <div>
//                      <p className="text-[10px] font-bold uppercase tracking-wider text-blue-600 mb-0.5">{r.condition}</p>
//                      <p className="text-[12px] font-medium text-slate-800 leading-snug">{r.action}</p>
//                    </div>
//                 </div>
//              ))
//            ) : (
//               <p className="text-[12px] text-slate-500">Awaiting clinical conditions to generate recommendations.</p>
//            )}
//         </div>
//       </div>

//         {/* 3. Timeline Panel */}
//         <div className="flex-[0.8] flex flex-col min-w-0 h-full">
//           <h3 className="font-serif text-[#1e1a17] text-[16px] mb-4 flex items-center gap-2">
//              <Clock size={16} className="text-[#b46b41]"/> Timeline
//           </h3>
//         <div className="flex-1 overflow-y-auto pr-2 custom-scrollbar relative">
//            <div className="absolute left-[7px] top-2 bottom-2 w-px bg-slate-200 z-0"></div>
//            <div className="flex flex-col gap-4 relative z-10">
//               {analysis.timeline && analysis.timeline.length > 0 ? (
//                 analysis.timeline.map((t, idx) => (
//                    <div key={idx} className="flex gap-3">
//                       <div className="w-3.5 h-3.5 rounded-full bg-slate-800 border-2 border-white shrink-0 mt-1 shadow-sm"></div>
//                       <div>
//                          <p className="text-[10px] font-bold font-mono text-slate-400 mb-0.5">{new Date(t.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</p>
//                          <p className="text-[12px] font-medium text-slate-700 leading-snug">{t.event}</p>
//                       </div>
//                    </div>
//                 ))
//               ) : (
//                  <p className="text-[12px] text-slate-500 ml-4">Timeline building...</p>
//               )}
//            </div>
//         </div>
//         </div>
//       </div>
//     </div>
//   );
// }


import React, { useState, useEffect } from 'react';
import { useOutletContext } from 'react-router-dom';
import { AlertTriangle, Activity, CheckCircle2, ChevronRight, CheckSquare, Clock } from 'lucide-react';

export default function IntelligencePanel() {
  const { data, timeWindow, setTimeWindow, loadingHistory } = useOutletContext();
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchIntelligence = async () => {
      setLoading(true);
      try {
        const res = await fetch(`https://icu-ai-monitor-d6z0.onrender.com/api/v1/analysis/?window=${timeWindow}`);
        const json = await res.json();
        setAnalysis(json);
      } catch (err) {
        console.error(err);
      }
      setLoading(false);
    };

    fetchIntelligence();
    const interval = setInterval(fetchIntelligence, 30000);
    return () => clearInterval(interval);
  }, [timeWindow]);

  if ((loading || loadingHistory) && !analysis) {
    return (
      <div style={{
        background: '#ffffff',
        borderRadius: 16,
        height: 400,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        boxShadow: '0 1px 4px rgba(0,0,0,0.06)',
        fontFamily: "'Inter', -apple-system, sans-serif",
      }}>
        <p style={{ fontSize: 13, color: '#94a3b8', margin: 0 }}>Loading Clinical Intelligence…</p>
      </div>
    );
  }

  if (!analysis) return null;

  return (
    <div style={{
      background: '#ffffff',
      borderRadius: 16,
      padding: '24px',
      boxShadow: '0 1px 4px rgba(0,0,0,0.06)',
      height: 400,
      display: 'flex',
      flexDirection: 'column',
      gap: 0,
      fontFamily: "'Inter', -apple-system, sans-serif",
    }}>

      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 20 }}>
        <h2 style={{ fontSize: 15, fontWeight: 700, color: '#0f172a', margin: 0 }}>
          Clinical Intelligence &amp; Events
        </h2>
        <div style={{
          display: 'flex', gap: 3,
          background: '#f8fafc', borderRadius: 10, padding: 3,
          border: '1px solid #f1f5f9',
        }}>
          {[15, 30, 60].map((w) => (
            <button
              key={w}
              onClick={() => setTimeWindow(w)}
              style={{
                fontSize: 11, fontWeight: 600,
                padding: '5px 12px', borderRadius: 8, border: 'none',
                cursor: 'pointer', fontFamily: 'inherit',
                background: timeWindow === w ? '#ffffff' : 'transparent',
                color: timeWindow === w ? '#0f172a' : '#94a3b8',
                boxShadow: timeWindow === w ? '0 1px 3px rgba(0,0,0,0.08)' : 'none',
                transition: 'all 0.15s',
              }}
            >
              {w}m
            </button>
          ))}
        </div>
      </div>

      {/* Three columns */}
      <div style={{ display: 'flex', flex: 1, gap: 0, overflow: 'hidden' }}>

        {/* ── 1. Critical Events ── */}
        <div style={{
          flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0,
          paddingRight: 24, borderRight: '1px solid #f1f5f9',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 7, marginBottom: 14 }}>
            <AlertTriangle size={13} color="#f59e0b" />
            <h3 style={{ fontSize: 12, fontWeight: 700, color: '#0f172a', margin: 0, letterSpacing: 0.2 }}>
              Critical Events
            </h3>
          </div>

          <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 8 }}>
            {analysis.events && analysis.events.length > 0 ? (
              analysis.events.slice(0, 5).map((e, idx) => (
                <div key={idx} style={{
                  padding: '10px 12px',
                  borderRadius: 10,
                  border: `1px solid ${e.severity === 'CRITICAL' ? '#fecaca' : '#fde68a'}`,
                  background: e.severity === 'CRITICAL' ? '#fef2f2' : '#fffbeb',
                  display: 'flex', alignItems: 'flex-start', gap: 10,
                }}>
                  <div style={{
                    width: 24, height: 24, borderRadius: '50%', flexShrink: 0,
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    background: e.severity === 'CRITICAL' ? '#fee2e2' : '#fef3c7',
                    color: e.severity === 'CRITICAL' ? '#dc2626' : '#d97706',
                    marginTop: 1,
                  }}>
                    {e.type.includes('HR')
                      ? <Activity size={11} />
                      : <AlertTriangle size={11} />}
                  </div>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 3 }}>
                      <p style={{ fontSize: 9, fontWeight: 700, textTransform: 'uppercase', letterSpacing: 1, color: '#94a3b8', margin: 0 }}>
                        {e.type.replace('_', ' ')}
                      </p>
                      <span style={{
                        fontSize: 8, fontWeight: 700, letterSpacing: 0.8,
                        padding: '1px 5px', borderRadius: 4,
                        background: e.severity === 'CRITICAL' ? '#dc2626' : '#f59e0b',
                        color: '#ffffff',
                      }}>
                        P{e.priority}
                      </span>
                    </div>
                    <p style={{ fontSize: 11, fontWeight: 500, color: '#1e293b', margin: '0 0 3px', lineHeight: 1.4 }}>
                      {e.description}
                    </p>
                    <p style={{ fontSize: 9, color: '#94a3b8', margin: 0, fontFamily: 'monospace' }}>
                      {new Date(e.timestamp).toLocaleTimeString()}
                    </p>
                  </div>
                </div>
              ))
            ) : (
              <div style={{
                padding: '12px 14px', borderRadius: 10,
                border: '1px solid #f1f5f9', background: '#f8fafc',
                display: 'flex', alignItems: 'center', gap: 8,
              }}>
                <CheckCircle2 size={14} color="#22c55e" />
                <p style={{ fontSize: 12, color: '#475569', margin: 0, fontWeight: 500 }}>
                  No critical events in current window.
                </p>
              </div>
            )}
          </div>
        </div>

        {/* ── 2. Recommendations ── */}
        <div style={{
          flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0,
          padding: '0 24px', borderRight: '1px solid #f1f5f9',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 7, marginBottom: 14 }}>
            <CheckSquare size={13} color="#3b82f6" />
            <h3 style={{ fontSize: 12, fontWeight: 700, color: '#0f172a', margin: 0 }}>
              Recommendations
            </h3>
          </div>

          <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 8 }}>
            {analysis.recommendations && analysis.recommendations.length > 0 ? (
              analysis.recommendations.map((r, idx) => (
                <div key={idx} style={{
                  padding: '10px 12px', borderRadius: 10,
                  border: '1px solid #dbeafe', background: '#eff6ff',
                  display: 'flex', alignItems: 'flex-start', gap: 8,
                }}>
                  <ChevronRight size={13} color="#3b82f6" style={{ marginTop: 2, flexShrink: 0 }} />
                  <div>
                    <p style={{ fontSize: 9, fontWeight: 700, textTransform: 'uppercase', letterSpacing: 1, color: '#3b82f6', margin: '0 0 3px' }}>
                      {r.condition}
                    </p>
                    <p style={{ fontSize: 11, fontWeight: 500, color: '#1e293b', margin: 0, lineHeight: 1.4 }}>
                      {r.action}
                    </p>
                  </div>
                </div>
              ))
            ) : (
              <p style={{ fontSize: 12, color: '#94a3b8', margin: 0 }}>
                Awaiting clinical conditions to generate recommendations.
              </p>
            )}
          </div>
        </div>

        {/* ── 3. Timeline ── */}
        <div style={{
          flex: 0.8, display: 'flex', flexDirection: 'column', minWidth: 0,
          paddingLeft: 24,
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 7, marginBottom: 14 }}>
            <Clock size={13} color="#8b5cf6" />
            <h3 style={{ fontSize: 12, fontWeight: 700, color: '#0f172a', margin: 0 }}>
              Timeline
            </h3>
          </div>

          <div style={{ flex: 1, overflowY: 'auto', position: 'relative' }}>
            {/* Vertical line */}
            <div style={{
              position: 'absolute', left: 5, top: 6, bottom: 6,
              width: 1, background: '#e2e8f0',
            }} />

            <div style={{ display: 'flex', flexDirection: 'column', gap: 16, position: 'relative', zIndex: 1 }}>
              {analysis.timeline && analysis.timeline.length > 0 ? (
                analysis.timeline.map((t, idx) => (
                  <div key={idx} style={{ display: 'flex', gap: 12, alignItems: 'flex-start' }}>
                    {/* Dot */}
                    <div style={{
                      width: 11, height: 11, borderRadius: '50%', flexShrink: 0,
                      background: '#1e293b', border: '2px solid #ffffff',
                      boxShadow: '0 0 0 1px #e2e8f0',
                      marginTop: 2,
                    }} />
                    <div>
                      <p style={{ fontSize: 9, fontWeight: 600, color: '#94a3b8', margin: '0 0 2px', fontFamily: 'monospace', letterSpacing: 0.5 }}>
                        {new Date(t.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </p>
                      <p style={{ fontSize: 11, fontWeight: 500, color: '#374151', margin: 0, lineHeight: 1.4 }}>
                        {t.event}
                      </p>
                    </div>
                  </div>
                ))
              ) : (
                <p style={{ fontSize: 12, color: '#94a3b8', margin: '0 0 0 20px' }}>Timeline building…</p>
              )}
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
