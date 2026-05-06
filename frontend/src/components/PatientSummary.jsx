// import { useEffect, useState } from 'react';
// import { API } from '../services/api';

// export default function PatientSummary({ riskLevel }) {
//   const [summary, setSummary] = useState('Initializing AI clinical analysis…');
//   const [loading, setLoading] = useState(false);
//   const [lastUpdated, setLastUpdated] = useState(null);

//   const fetchSummary = async () => {
//     setLoading(true);
//     try {
//       const data = await API.getSummary();
//       setSummary(data.summary || 'No summary available.');
//       setLastUpdated(new Date().toLocaleTimeString());
//     } catch {
//       setSummary('Unable to connect to AI summarizer. Please ensure the backend is running.');
//     } finally {
//       setLoading(false);
//     }
//   };

//   // Refresh summary every 10 seconds
//   useEffect(() => {
//     fetchSummary();
//     const interval = setInterval(fetchSummary, 10_000);
//     return () => clearInterval(interval);
//   }, []);

//   const borderColor =
//     riskLevel === 'HIGH' ? '#ff4d6d' : riskLevel === 'MODERATE' ? '#ffb347' : '#00d4ff';

//   return (
//     <div className="patient-summary" style={{ borderColor }}>
//       <div className="patient-summary__header">
//         <span className="patient-summary__icon">⬡</span>
//         <span className="patient-summary__title">AI Clinical Summary</span>
//         <button
//           className="patient-summary__refresh"
//           onClick={fetchSummary}
//           disabled={loading}
//           style={{ color: borderColor, borderColor }}
//         >
//           {loading ? '⟳ Analyzing…' : '↻ Refresh'}
//         </button>
//       </div>

//       <div className={`patient-summary__body ${loading ? 'loading' : ''}`}>
//         <p>{summary}</p>
//       </div>

//       {lastUpdated && (
//         <div className="patient-summary__footer">
//           Last updated: {lastUpdated}
//         </div>
//       )}
//     </div>
//   );
// }


import { useEffect, useState } from 'react';
import { API } from '../services/api';

export default function PatientSummary({ riskLevel }) {
  const [summary, setSummary] = useState('Initializing AI clinical analysis…');
  const [loading, setLoading] = useState(false);
  const [lastUpdated, setLastUpdated] = useState(null);

  const fetchSummary = async () => {
    setLoading(true);
    try {
      const data = await API.getSummary();
      setSummary(data.summary || 'No summary available.');
      setLastUpdated(new Date().toLocaleTimeString());
    } catch {
      setSummary('Unable to connect to AI summarizer. Please ensure the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSummary();
    const interval = setInterval(fetchSummary, 10_000);
    return () => clearInterval(interval);
  }, []);

  const riskColor = riskLevel === 'HIGH' ? '#dc2626'
    : riskLevel === 'MODERATE' ? '#d97706'
      : '#16a34a';
  const riskBg = riskLevel === 'HIGH' ? '#fef2f2'
    : riskLevel === 'MODERATE' ? '#fffbeb'
      : '#f0fdf4';
  const riskBorder = riskLevel === 'HIGH' ? '#fecaca'
    : riskLevel === 'MODERATE' ? '#fde68a'
      : '#bbf7d0';
  const riskLabel = riskLevel === 'HIGH' ? 'HIGH'
    : riskLevel === 'MODERATE' ? 'MODERATE'
      : 'LOW';

  return (
    <div style={{
      background: '#ffffff',
      borderRadius: 16,
      padding: '24px',
      boxShadow: '0 1px 4px rgba(0,0,0,0.06)',
      display: 'flex',
      flexDirection: 'column',
      fontFamily: "'Inter', -apple-system, sans-serif",
    }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          {/* Icon */}
          <div style={{
            width: 32, height: 32, borderRadius: 8,
            background: '#f0f4ff',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: 14, color: '#6366f1',
          }}>
            ✦
          </div>
          <div>
            <p style={{ fontSize: 9, fontWeight: 700, textTransform: 'uppercase', letterSpacing: 2, color: '#94a3b8', margin: '0 0 2px' }}>
              Clinical Note
            </p>
            <h3 style={{ fontSize: 15, fontWeight: 700, color: '#0f172a', margin: 0 }}>AI Summary</h3>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <span style={{
            display: 'inline-flex', alignItems: 'center', gap: 5,
            fontSize: 9, fontWeight: 700, letterSpacing: 1.2, textTransform: 'uppercase',
            padding: '4px 10px', borderRadius: 20,
            color: riskColor, background: riskBg, border: `1px solid ${riskBorder}`,
          }}>
            ✦ {riskLabel}
          </span>
          <button
            onClick={fetchSummary}
            disabled={loading}
            style={{
              width: 30, height: 30,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              background: '#f8fafc', border: '1px solid #e2e8f0',
              borderRadius: 8, cursor: 'pointer',
              fontSize: 13, color: '#94a3b8',
              transition: 'all 0.15s',
              animation: loading ? 'spin 1s linear infinite' : 'none',
            }}
            title="Refresh summary"
          >
            ↻
          </button>
        </div>
      </div>

      {/* Summary body */}
      <div style={{
        background: '#f8fafc',
        border: '1px solid #f1f5f9',
        borderRadius: 10,
        padding: '16px',
        marginBottom: 16,
        minHeight: 80,
      }}>
        <p style={{
          fontSize: 13, color: loading ? '#94a3b8' : '#1e293b',
          margin: 0, lineHeight: 1.7,
          fontStyle: loading ? 'italic' : 'normal',
          transition: 'color 0.2s',
        }}>
          {summary}
        </p>
      </div>

      {/* Footer */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span style={{ fontSize: 10, color: '#94a3b8', fontFamily: 'monospace' }}>
          Model: rule-based-v1 (mock)
        </span>
        {lastUpdated && (
          <span style={{ fontSize: 10, color: '#94a3b8', fontFamily: 'monospace' }}>
            Updated {lastUpdated}
          </span>
        )}
      </div>

      <style>{`
        @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
      `}</style>
    </div>
  );
}