// import React, { useState, useEffect } from 'react';
// import { useOutletContext } from 'react-router-dom';
// import { Activity, AlertTriangle, CheckCircle2, TrendingDown, TrendingUp, Minus } from 'lucide-react';

// export default function AIInsightPanel({ metric }) {
//   const { timeWindow, setTimeWindow } = useOutletContext();
//   const [analysis, setAnalysis] = useState(null);
//   const [loading, setLoading] = useState(false);

//   useEffect(() => {
//     const fetchAnalysis = async () => {
//       setLoading(true);
//       try {
//         const url = metric
//           ? `http://localhost:8000/api/v1/analysis/?window=${timeWindow}&metric=${metric}`
//           : `http://localhost:8000/api/v1/analysis/?window=${timeWindow}`;
//         const res = await fetch(url);
//         const data = await res.json();
//         setAnalysis(data);
//       } catch (err) {
//         console.error(err);
//       }
//       setLoading(false);
//     };

//     fetchAnalysis();
//     const interval = setInterval(fetchAnalysis, 30000);
//     return () => clearInterval(interval);
//   }, [timeWindow, metric]);

//   const getTrendIcon = (t) => {
//     if (t === 'increasing' || t === 'worsening') return <TrendingUp size={14} />;
//     if (t === 'decreasing') return <TrendingDown size={14} />;
//     return <Minus size={14} />;
//   };

//   return (
//     <div className="bg-white rounded-[24px] p-8 shadow-[0_2px_14px_-6px_rgba(0,0,0,0.06)] h-full flex flex-col min-h-[360px]">

//       <div className="flex items-center justify-between mb-6">
//         <div className="flex items-center gap-3">
//           <h3 className="font-serif text-[#1e1a17] text-[19px]">Intelligent Analysis</h3>
//           {analysis && analysis.risk_level && (
//             <span className={`px-2.5 py-1 text-[10px] font-bold uppercase tracking-wider rounded-full flex items-center gap-1.5 ${analysis.risk_level === 'CRITICAL' ? 'bg-red-100 text-red-700' :
//                 analysis.risk_level === 'WARNING' ? 'bg-orange-100 text-orange-700' :
//                   'bg-emerald-100 text-emerald-700'
//               }`}>
//               {analysis.risk_level === 'CRITICAL' ? <AlertTriangle size={12} /> :
//                 analysis.risk_level === 'WARNING' ? <Activity size={12} /> :
//                   <CheckCircle2 size={12} />}
//               {analysis.risk_level}
//             </span>
//           )}
//         </div>

//         <div className="flex gap-4">
//           {[15, 30, 60].map((w) => (
//             <button
//               key={w}
//               onClick={() => setTimeWindow(w)}
//               className={`text-[11px] font-semibold tracking-wider transition-colors ${timeWindow === w ? 'text-[#b46b41]' : 'text-[#a2998d] hover:text-[#1e1a17]'}`}
//             >
//               {w} Min
//             </button>
//           ))}
//         </div>
//       </div>

//       <div className="flex-1 flex flex-col justify-center h-full">
//         {loading && !analysis ? (
//           <p className="text-sm text-[#8c8273] text-center w-full">Generating intelligent insights...</p>
//         ) : analysis ? (
//           <div className="w-full flex flex-col gap-5">

//             <div className="grid grid-cols-1 gap-4">
//               <div className="bg-slate-50 rounded-xl p-4 border border-slate-100">
//                 <h4 className="text-[10px] uppercase tracking-wider font-bold text-slate-400 mb-1.5">Key Observation</h4>
//                 <p className="text-[13px] font-medium text-slate-800 leading-relaxed">
//                   {analysis.key_observation || "Insufficient data for detailed observation."}
//                 </p>
//               </div>

//               <div className="grid grid-cols-2 gap-4">
//                 <div className="bg-slate-50 rounded-xl p-4 border border-slate-100">
//                   <h4 className="text-[10px] uppercase tracking-wider font-bold text-slate-400 mb-1.5">Possible Cause</h4>
//                   <p className="text-[12px] text-slate-700 leading-snug">
//                     {analysis.possible_cause || "N/A"}
//                   </p>
//                 </div>

//                 <div className="bg-slate-50 rounded-xl p-4 border border-slate-100">
//                   <h4 className="text-[10px] uppercase tracking-wider font-bold text-slate-400 mb-1.5">Prediction</h4>
//                   <p className="text-[12px] text-slate-700 leading-snug">
//                     {analysis.prediction || "N/A"}
//                   </p>
//                 </div>
//               </div>
//             </div>

//             <div className="flex items-center justify-between px-2 pt-2 border-t border-slate-100">
//               <div className="flex items-center gap-2">
//                 <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Confidence Score:</span>
//                 <span className={`text-[12px] font-bold ${analysis.confidence_score > 0.7 ? 'text-emerald-600' : analysis.confidence_score > 0.4 ? 'text-orange-500' : 'text-slate-500'}`}>
//                   {Math.round((analysis.confidence_score || 0) * 100)}%
//                 </span>
//               </div>

//               <div className="flex items-center gap-4">
//                 {metric && analysis.metrics && analysis.metrics[metric] ? (
//                   <div className="flex items-center gap-3 text-[11px] uppercase font-bold tracking-wider text-slate-500">
//                     <span>Avg: <span className="text-slate-800">{Math.round(analysis.metrics[metric].avg)}</span></span>
//                     <span className="flex items-center gap-1">
//                       Trend:
//                       <span className={`flex items-center gap-0.5 ${analysis.metrics[metric].trend === 'stable' ? 'text-slate-800' :
//                           ((metric === 'spo2' && analysis.metrics[metric].trend === 'decreasing') ||
//                             ((metric === 'heart_rate' || metric === 'bp') && analysis.metrics[metric].trend === 'increasing'))
//                             ? 'text-orange-500' : 'text-green-600'
//                         }`}>
//                         {analysis.metrics[metric].trend} {getTrendIcon(analysis.metrics[metric].trend)}
//                       </span>
//                     </span>
//                   </div>
//                 ) : (
//                   <div className="flex items-center gap-1 text-[11px] uppercase font-bold tracking-wider text-slate-500">
//                     Overall Trend:
//                     <span className={`flex items-center gap-0.5 ml-1 ${analysis.trend === 'worsening' ? 'text-orange-500' : analysis.trend === 'improving' ? 'text-green-600' : 'text-slate-800'}`}>
//                       {analysis.trend} {getTrendIcon(analysis.trend)}
//                     </span>
//                   </div>
//                 )}
//               </div>
//             </div>

//           </div>
//         ) : (
//           <p className="text-sm text-[#8c8273] text-center w-full">No analysis available.</p>
//         )}
//       </div>

//     </div>
//   );
// }


import React, { useState, useEffect } from 'react';
import { useOutletContext } from 'react-router-dom';
import { Activity, AlertTriangle, CheckCircle2, TrendingDown, TrendingUp, Minus } from 'lucide-react';

export default function AIInsightPanel({ metric }) {
  const { timeWindow, setTimeWindow } = useOutletContext();
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchAnalysis = async () => {
      setLoading(true);
      try {
        const url = metric
          ? `https://icu-ai-monitor-d6z0.onrender.com`
          : `https://icu-ai-monitor-d6z0.onrender.com`;
        const res = await fetch(url);
        const data = await res.json();
        setAnalysis(data);
      } catch (err) {
        console.error(err);
      }
      setLoading(false);
    };

    fetchAnalysis();
    const interval = setInterval(fetchAnalysis, 30000);
    return () => clearInterval(interval);
  }, [timeWindow, metric]);

  const getTrendIcon = (t) => {
    if (t === 'increasing' || t === 'worsening') return <TrendingUp size={12} />;
    if (t === 'decreasing') return <TrendingDown size={12} />;
    return <Minus size={12} />;
  };

  const riskColor = analysis?.risk_level === 'CRITICAL' ? '#dc2626'
    : analysis?.risk_level === 'WARNING' ? '#d97706'
      : '#16a34a';
  const riskBg = analysis?.risk_level === 'CRITICAL' ? '#fef2f2'
    : analysis?.risk_level === 'WARNING' ? '#fffbeb'
      : '#f0fdf4';
  const riskBorder = analysis?.risk_level === 'CRITICAL' ? '#fecaca'
    : analysis?.risk_level === 'WARNING' ? '#fde68a'
      : '#bbf7d0';

  return (
    <div style={{
      background: '#ffffff',
      borderRadius: 16,
      padding: '24px',
      boxShadow: '0 1px 4px rgba(0,0,0,0.06)',
      height: '100%',
      display: 'flex',
      flexDirection: 'column',
      minHeight: 360,
      fontFamily: "'Inter', -apple-system, sans-serif",
    }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 20 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <h3 style={{ fontSize: 15, fontWeight: 700, color: '#0f172a', margin: 0 }}>Intelligent Analysis</h3>
          {analysis?.risk_level && (
            <span style={{
              display: 'inline-flex', alignItems: 'center', gap: 5,
              fontSize: 9, fontWeight: 700, letterSpacing: 1.2, textTransform: 'uppercase',
              padding: '3px 10px', borderRadius: 20,
              color: riskColor, background: riskBg, border: `1px solid ${riskBorder}`,
            }}>
              {analysis.risk_level === 'CRITICAL' ? <AlertTriangle size={10} /> :
                analysis.risk_level === 'WARNING' ? <Activity size={10} /> :
                  <CheckCircle2 size={10} />}
              {analysis.risk_level}
            </span>
          )}
        </div>

        {/* Time window pills */}
        <div style={{ display: 'flex', gap: 4, background: '#f8fafc', borderRadius: 10, padding: 3 }}>
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

      {/* Content */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
        {loading && !analysis ? (
          <p style={{ fontSize: 13, color: '#94a3b8', textAlign: 'center', margin: 0 }}>Generating intelligent insights…</p>
        ) : analysis ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>

            {/* Key Observation */}
            <div style={{
              background: '#f8fafc', borderRadius: 10, padding: '14px 16px',
              border: '1px solid #f1f5f9',
            }}>
              <p style={{ fontSize: 9, fontWeight: 700, textTransform: 'uppercase', letterSpacing: 1.5, color: '#94a3b8', margin: '0 0 6px' }}>
                Key Observation
              </p>
              <p style={{ fontSize: 13, fontWeight: 500, color: '#1e293b', margin: 0, lineHeight: 1.6 }}>
                {analysis.key_observation || 'Insufficient data for detailed observation.'}
              </p>
            </div>

            {/* Cause + Prediction */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
              <div style={{ background: '#f8fafc', borderRadius: 10, padding: '14px 16px', border: '1px solid #f1f5f9' }}>
                <p style={{ fontSize: 9, fontWeight: 700, textTransform: 'uppercase', letterSpacing: 1.5, color: '#94a3b8', margin: '0 0 6px' }}>
                  Possible Cause
                </p>
                <p style={{ fontSize: 12, color: '#475569', margin: 0, lineHeight: 1.5 }}>
                  {analysis.possible_cause || 'N/A'}
                </p>
              </div>
              <div style={{ background: '#f8fafc', borderRadius: 10, padding: '14px 16px', border: '1px solid #f1f5f9' }}>
                <p style={{ fontSize: 9, fontWeight: 700, textTransform: 'uppercase', letterSpacing: 1.5, color: '#94a3b8', margin: '0 0 6px' }}>
                  Prediction
                </p>
                <p style={{ fontSize: 12, color: '#475569', margin: 0, lineHeight: 1.5 }}>
                  {analysis.prediction || 'N/A'}
                </p>
              </div>
            </div>

            {/* Footer row */}
            <div style={{
              display: 'flex', alignItems: 'center', justifyContent: 'space-between',
              paddingTop: 12, borderTop: '1px solid #f1f5f9',
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                <span style={{ fontSize: 10, fontWeight: 600, color: '#94a3b8', textTransform: 'uppercase', letterSpacing: 1 }}>
                  Confidence:
                </span>
                <span style={{
                  fontSize: 12, fontWeight: 700,
                  color: analysis.confidence_score > 0.7 ? '#16a34a'
                    : analysis.confidence_score > 0.4 ? '#d97706'
                      : '#94a3b8',
                }}>
                  {Math.round((analysis.confidence_score || 0) * 100)}%
                </span>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 11, color: '#94a3b8', fontWeight: 600, textTransform: 'uppercase', letterSpacing: 0.8 }}>
                {metric && analysis.metrics?.[metric] ? (
                  <>
                    <span>Avg: <span style={{ color: '#1e293b' }}>{Math.round(analysis.metrics[metric].avg)}</span></span>
                    <span style={{ color: '#e2e8f0' }}>·</span>
                    <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                      Trend:
                      <span style={{
                        display: 'flex', alignItems: 'center', gap: 3, marginLeft: 2,
                        color: analysis.metrics[metric].trend === 'stable' ? '#1e293b'
                          : ((metric === 'spo2' && analysis.metrics[metric].trend === 'decreasing') ||
                            ((metric === 'heart_rate' || metric === 'bp') && analysis.metrics[metric].trend === 'increasing'))
                            ? '#d97706' : '#16a34a',
                      }}>
                        {analysis.metrics[metric].trend} {getTrendIcon(analysis.metrics[metric].trend)}
                      </span>
                    </span>
                  </>
                ) : (
                  <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                    Overall Trend:
                    <span style={{
                      display: 'flex', alignItems: 'center', gap: 3, marginLeft: 2,
                      color: analysis.trend === 'worsening' ? '#d97706'
                        : analysis.trend === 'improving' ? '#16a34a'
                          : '#1e293b',
                    }}>
                      {analysis.trend} {getTrendIcon(analysis.trend)}
                    </span>
                  </span>
                )}
              </div>
            </div>

          </div>
        ) : (
          <p style={{ fontSize: 13, color: '#94a3b8', textAlign: 'center', margin: 0 }}>No analysis available.</p>
        )}
      </div>
    </div>
  );
}
