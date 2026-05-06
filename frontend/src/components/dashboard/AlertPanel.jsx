// import React, { useState, useEffect } from 'react';
// import { Download } from 'lucide-react';
// import { downloadCSV } from '../../utils/csvExport';

// export default function AlertPanel() {
//   const [alerts, setAlerts] = useState([]);
//   const [explanation, setExplanation] = useState("");

//   useEffect(() => {
//     const fetchData = async () => {
//       try {
//         const resAlerts = await fetch('http://localhost:8000/api/v1/vitals/alerts?limit=5');
//         const dataAlerts = await resAlerts.json();
//         setAlerts(dataAlerts);

//         const resAnalysis = await fetch('http://localhost:8000/api/v1/analysis/?window=15');
//         const dataAnalysis = await resAnalysis.json();
//         setExplanation(dataAnalysis.alert_explanation || "");
//       } catch (err) {
//         console.error(err);
//       }
//     };

//     fetchData();
//     const interval = setInterval(fetchData, 10000);
//     return () => clearInterval(interval);
//   }, []);

//   const handleDownloadCSV = () => {
//     const csvData = alerts.map(alert => ({
//       timestamp: new Date(alert.timestamp).toISOString(),
//       vital_type: alert.vital_type,
//       value: alert.value,
//       severity: alert.severity,
//       reason: alert.reason
//     }));
//     downloadCSV(csvData, 'system_alerts.csv');
//   };

//   return (
//     <div className="bg-white rounded-[24px] p-8 shadow-[0_2px_14px_-6px_rgba(0,0,0,0.06)] h-full flex flex-col min-h-[300px]">
//       <div className="flex justify-between items-center mb-6">
//         <h3 className="font-serif text-[#1e1a17] text-[19px]">System Notifications</h3>
//         <button
//           onClick={handleDownloadCSV}
//           className="flex items-center gap-2 text-[12px] font-medium bg-slate-100 text-slate-700 px-3 py-1.5 rounded-xl shadow-sm hover:bg-slate-200 transition-colors"
//         >
//           <Download size={14} />
//           Export CSV
//         </button>
//       </div>

//       {explanation && (
//         <div className={`mb-6 p-4 rounded-xl border ${explanation.includes('CRITICAL') ? 'bg-red-50 border-red-100 text-red-800' : explanation.includes('WARNING') ? 'bg-orange-50 border-orange-100 text-orange-800' : 'bg-slate-50 border-slate-100 text-slate-600'}`}>
//           <p className="text-[10px] font-bold uppercase tracking-wider mb-1 opacity-70">Current Intelligence Status</p>
//           <p className="text-[13px] font-medium leading-snug">{explanation}</p>
//         </div>
//       )}

//       <div className="flex-1 overflow-y-auto pr-2 flex flex-col">
//         {alerts.length === 0 ? (
//           <div className="w-full text-center my-auto">
//             <p className="text-[13px] text-[#8c8273]">No notifications yet.</p>
//           </div>
//         ) : (
//           <div className="space-y-4 h-full pt-1">
//             {alerts.map((alert) => (
//               <div key={alert.id} className="flex gap-4 items-center border-b border-[#f0ece5] pb-3 last:border-0 last:pb-0">
//                 <div className={`w-2 h-2 rounded-full shrink-0 ${alert.severity === 'CRITICAL' ? 'bg-[#e13f28]' : 'bg-[#e0912f]'}`}></div>
//                 <div className="flex-1 flex flex-col gap-1">
//                   <div className="flex justify-between items-center gap-4">
//                     <p className="text-[12px] text-[#38332f] leading-snug font-medium">
//                       <span className="font-bold mr-1">{alert.vital_type} = {alert.value} {alert.vital_type === 'HR' ? 'bpm' : alert.vital_type === 'SpO2' ? '%' : alert.vital_type === 'BP' ? 'mmHg' : ''}</span>
//                     </p>
//                     <p className="text-[10px] text-[#a2998d] font-semibold whitespace-nowrap">{new Date(alert.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</p>
//                   </div>
//                   <div className="flex items-center gap-2">
//                     <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${alert.severity === 'CRITICAL' ? 'bg-red-100 text-red-700' : 'bg-orange-100 text-orange-700'}`}>{alert.severity}</span>
//                     <span className="text-[11px] text-slate-500">{alert.reason}</span>
//                   </div>
//                 </div>
//               </div>
//             ))}
//           </div>
//         )}
//       </div>
//     </div>
//   );
// }


import React, { useState, useEffect } from 'react';
import { Download } from 'lucide-react';
import { downloadCSV } from '../../utils/csvExport';

export default function AlertPanel() {
  const [alerts, setAlerts] = useState([]);
  const [explanation, setExplanation] = useState("");

  useEffect(() => {
    const fetchData = async () => {
      try {
        const resAlerts = await fetch('http://localhost:8000/api/v1/vitals/alerts?limit=5');
        const dataAlerts = await resAlerts.json();
        setAlerts(dataAlerts);

        const resAnalysis = await fetch('http://localhost:8000/api/v1/analysis/?window=15');
        const dataAnalysis = await resAnalysis.json();
        setExplanation(dataAnalysis.alert_explanation || "");
      } catch (err) {
        console.error(err);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 10000);
    return () => clearInterval(interval);
  }, []);

  const handleDownloadCSV = () => {
    const csvData = alerts.map(alert => ({
      timestamp: new Date(alert.timestamp).toISOString(),
      vital_type: alert.vital_type,
      value: alert.value,
      severity: alert.severity,
      reason: alert.reason
    }));
    downloadCSV(csvData, 'system_alerts.csv');
  };

  return (
    <div style={{
      background: '#ffffff',
      borderRadius: 16,
      padding: '24px',
      boxShadow: '0 1px 4px rgba(0,0,0,0.06)',
      height: '100%',
      display: 'flex',
      flexDirection: 'column',
      minHeight: 300,
      fontFamily: "'Inter', -apple-system, sans-serif",
    }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
        <h3 style={{ fontSize: 15, fontWeight: 700, color: '#0f172a', margin: 0 }}>System Notifications</h3>
        <button
          onClick={handleDownloadCSV}
          style={{
            display: 'flex', alignItems: 'center', gap: 6,
            fontSize: 11, fontWeight: 600,
            background: '#f8fafc', color: '#475569',
            border: '1px solid #e2e8f0',
            padding: '6px 12px', borderRadius: 8,
            cursor: 'pointer', fontFamily: 'inherit',
          }}
        >
          <Download size={12} />
          Export CSV
        </button>
      </div>

      {/* Intelligence Status banner */}
      {explanation && (
        <div style={{
          marginBottom: 16,
          padding: '10px 14px',
          borderRadius: 10,
          background: explanation.includes('CRITICAL') ? '#fef2f2' : explanation.includes('WARNING') ? '#fffbeb' : '#f8fafc',
          border: `1px solid ${explanation.includes('CRITICAL') ? '#fecaca' : explanation.includes('WARNING') ? '#fde68a' : '#e2e8f0'}`,
        }}>
          <p style={{ fontSize: 9, fontWeight: 700, textTransform: 'uppercase', letterSpacing: 1.5, color: '#94a3b8', margin: '0 0 4px' }}>
            Current Intelligence Status
          </p>
          <p style={{
            fontSize: 12, fontWeight: 500, margin: 0, lineHeight: 1.5,
            color: explanation.includes('CRITICAL') ? '#dc2626' : explanation.includes('WARNING') ? '#d97706' : '#475569',
          }}>
            {explanation}
          </p>
        </div>
      )}

      {/* Alerts list */}
      <div style={{ flex: 1, overflowY: 'auto' }}>
        {alerts.length === 0 ? (
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%' }}>
            <p style={{ fontSize: 13, color: '#94a3b8', margin: 0 }}>No notifications yet.</p>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 0 }}>
            {alerts.map((alert, idx) => (
              <div key={alert.id} style={{
                display: 'flex', gap: 12, alignItems: 'flex-start',
                padding: '12px 0',
                borderBottom: idx < alerts.length - 1 ? '1px solid #f1f5f9' : 'none',
              }}>
                {/* Severity dot */}
                <div style={{
                  width: 7, height: 7, borderRadius: '50%', marginTop: 4, flexShrink: 0,
                  background: alert.severity === 'CRITICAL' ? '#ef4444' : '#f59e0b',
                }} />

                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 }}>
                    <p style={{ fontSize: 12, fontWeight: 600, color: '#1e293b', margin: 0 }}>
                      {alert.vital_type} = {alert.value}{' '}
                      <span style={{ color: '#64748b', fontWeight: 400 }}>
                        {alert.vital_type === 'HR' ? 'bpm' : alert.vital_type === 'SpO2' ? '%' : alert.vital_type === 'BP' ? 'mmHg' : ''}
                      </span>
                    </p>
                    <span style={{ fontSize: 10, color: '#94a3b8', fontWeight: 500, whiteSpace: 'nowrap' }}>
                      {new Date(alert.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <span style={{
                      fontSize: 9, fontWeight: 700, letterSpacing: 1, textTransform: 'uppercase',
                      padding: '2px 8px', borderRadius: 20,
                      background: alert.severity === 'CRITICAL' ? '#fef2f2' : '#fffbeb',
                      color: alert.severity === 'CRITICAL' ? '#dc2626' : '#d97706',
                      border: `1px solid ${alert.severity === 'CRITICAL' ? '#fecaca' : '#fde68a'}`,
                    }}>
                      {alert.severity}
                    </span>
                    <span style={{ fontSize: 11, color: '#64748b' }}>{alert.reason}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

