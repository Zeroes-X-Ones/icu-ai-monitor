// const LEVEL_CONFIG = {
//   LOW: {
//     color: '#a8ff78',
//     glow: 'rgba(168,255,120,0.5)',
//     bg: 'rgba(168,255,120,0.08)',
//     icon: '✓',
//     message: 'Patient vitals stable. Continue routine monitoring.',
//   },
//   MODERATE: {
//     color: '#ffb347',
//     glow: 'rgba(255,179,71,0.5)',
//     bg: 'rgba(255,179,71,0.08)',
//     icon: '⚠',
//     message: 'Elevated physiological stress detected. Increased vigilance advised.',
//   },
//   HIGH: {
//     color: '#ff4d6d',
//     glow: 'rgba(255,77,109,0.6)',
//     bg: 'rgba(255,77,109,0.1)',
//     icon: '!',
//     message: 'Critical distress indicators present. Immediate clinical review required.',
//   },
// };

// export default function DistressMeter({ score = 0, riskLevel = 'LOW', triggeredRules = [] }) {
//   const cfg = LEVEL_CONFIG[riskLevel] || LEVEL_CONFIG.LOW;
//   const pct = Math.round(score * 100);

//   return (
//     <div
//       className="distress-meter"
//       style={{
//         '--dm-color': cfg.color,
//         '--dm-glow': cfg.glow,
//         background: cfg.bg,
//         borderColor: cfg.color,
//       }}
//     >
//       <div className="distress-meter__top">
//         <div className="distress-meter__label">Distress Score</div>
//         <div
//           className="distress-meter__badge"
//           style={{ color: cfg.color, borderColor: cfg.color, boxShadow: `0 0 12px ${cfg.glow}` }}
//         >
//           <span className="distress-meter__badge-icon">{cfg.icon}</span>
//           {riskLevel}
//         </div>
//       </div>

//       <div className="distress-meter__score" style={{ color: cfg.color }}>
//         {pct}
//         <span className="distress-meter__score-unit">/ 100</span>
//       </div>

//       {/* Progress bar */}
//       <div className="distress-meter__bar-track">
//         <div
//           className="distress-meter__bar-fill"
//           style={{
//             width: `${pct}%`,
//             background: `linear-gradient(90deg, ${cfg.color}88, ${cfg.color})`,
//             boxShadow: `0 0 10px ${cfg.glow}`,
//           }}
//         />
//         {/* Threshold markers */}
//         <div className="distress-meter__marker" style={{ left: '30%' }} title="MODERATE threshold" />
//         <div className="distress-meter__marker" style={{ left: '70%' }} title="HIGH threshold" />
//       </div>
//       <div className="distress-meter__scale">
//         <span style={{ color: '#a8ff78' }}>LOW</span>
//         <span style={{ color: '#ffb347' }}>MODERATE</span>
//         <span style={{ color: '#ff4d6d' }}>HIGH</span>
//       </div>

//       <p className="distress-meter__message" style={{ color: cfg.color }}>
//         {cfg.message}
//       </p>

//       {triggeredRules.length > 0 && (
//         <ul className="distress-meter__rules">
//           {triggeredRules.map((rule, i) => (
//             <li key={i} style={{ color: cfg.color }}>
//               ▸ {rule}
//             </li>
//           ))}
//         </ul>
//       )}
//     </div>
//   );
// }




const LEVEL_CONFIG = {
  LOW: {
    color: '#16a34a',
    trackColor: '#dcfce7',
    fillColor: '#22c55e',
    badgeBg: '#f0fdf4',
    badgeBorder: '#bbf7d0',
    message: 'Patient vitals stable. Continue routine 4-hourly observation.',
    label: 'LOW RISK',
  },
  MODERATE: {
    color: '#d97706',
    trackColor: '#fef3c7',
    fillColor: '#f59e0b',
    badgeBg: '#fffbeb',
    badgeBorder: '#fde68a',
    message: 'Elevated physiological stress detected. Increased vigilance advised.',
    label: 'MODERATE',
  },
  HIGH: {
    color: '#dc2626',
    trackColor: '#fee2e2',
    fillColor: '#ef4444',
    badgeBg: '#fef2f2',
    badgeBorder: '#fecaca',
    message: 'Critical distress indicators present. Immediate clinical review required.',
    label: 'HIGH RISK',
  },
};

export default function DistressMeter({ score = 0, riskLevel = 'LOW', triggeredRules = [] }) {
  const cfg = LEVEL_CONFIG[riskLevel] || LEVEL_CONFIG.LOW;
  const pct = Math.round(score * 100);

  return (
    <div style={{
      background: '#ffffff',
      borderRadius: 16,
      padding: '24px',
      boxShadow: '0 1px 4px rgba(0,0,0,0.06)',
      fontFamily: "'Inter', -apple-system, sans-serif",
    }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 20 }}>
        <div>
          <p style={{ fontSize: 9, fontWeight: 700, textTransform: 'uppercase', letterSpacing: 2, color: '#94a3b8', margin: '0 0 4px' }}>
            Distress Index
          </p>
          <h3 style={{ fontSize: 15, fontWeight: 700, color: '#0f172a', margin: 0 }}>
            Composite physiologic stress
          </h3>
        </div>
        <span style={{
          display: 'inline-flex', alignItems: 'center', gap: 5,
          fontSize: 9, fontWeight: 700, letterSpacing: 1.2, textTransform: 'uppercase',
          padding: '4px 10px', borderRadius: 20,
          color: cfg.color,
          background: cfg.badgeBg,
          border: `1px solid ${cfg.badgeBorder}`,
        }}>
          <span style={{ fontSize: 10 }}>⊙</span>
          {cfg.label}
        </span>
      </div>

      {/* Score display */}
      <div style={{ display: 'flex', alignItems: 'baseline', gap: 6, marginBottom: 20 }}>
        <span style={{ fontSize: 52, fontWeight: 700, color: cfg.color, lineHeight: 1, letterSpacing: -2 }}>
          {pct}
        </span>
        <span style={{ fontSize: 14, color: '#94a3b8', fontWeight: 500 }}>/ 100</span>
      </div>

      {/* Progress track */}
      <div style={{
        height: 6, borderRadius: 6,
        background: '#f1f5f9',
        position: 'relative',
        marginBottom: 8,
        overflow: 'visible',
      }}>
        {/* Fill */}
        <div style={{
          position: 'absolute', left: 0, top: 0, bottom: 0,
          width: `${pct}%`,
          background: cfg.fillColor,
          borderRadius: 6,
          transition: 'width 0.5s ease',
          minWidth: pct > 0 ? 6 : 0,
        }} />
        {/* Threshold ticks */}
        {[30, 70].map(pos => (
          <div key={pos} style={{
            position: 'absolute', top: -3, bottom: -3,
            left: `${pos}%`,
            width: 1,
            background: '#e2e8f0',
          }} />
        ))}
      </div>

      {/* Scale labels */}
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 18 }}>
        <span style={{ fontSize: 9, fontWeight: 600, color: '#94a3b8', letterSpacing: 1 }}>0 LOW</span>
        <span style={{ fontSize: 9, fontWeight: 600, color: '#94a3b8', letterSpacing: 1 }}>30</span>
        <span style={{ fontSize: 9, fontWeight: 600, color: '#94a3b8', letterSpacing: 1 }}>70</span>
        <span style={{ fontSize: 9, fontWeight: 600, color: '#94a3b8', letterSpacing: 1 }}>100 HIGH</span>
      </div>

      {/* Status message */}
      <p style={{ fontSize: 13, color: '#475569', margin: 0, lineHeight: 1.5 }}>
        {cfg.message}
      </p>

      {/* Triggered rules */}
      {triggeredRules.length > 0 && (
        <div style={{ marginTop: 14, paddingTop: 14, borderTop: '1px solid #f1f5f9' }}>
          {triggeredRules.map((rule, i) => (
            <div key={i} style={{
              display: 'flex', alignItems: 'center', gap: 8,
              fontSize: 11, color: '#64748b', padding: '3px 0',
            }}>
              <span style={{ color: cfg.color, fontSize: 9 }}>▸</span>
              {rule}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}