const LEVEL_CONFIG = {
  LOW: {
    color: '#a8ff78',
    glow: 'rgba(168,255,120,0.5)',
    bg: 'rgba(168,255,120,0.08)',
    icon: '✓',
    message: 'Patient vitals stable. Continue routine monitoring.',
  },
  MODERATE: {
    color: '#ffb347',
    glow: 'rgba(255,179,71,0.5)',
    bg: 'rgba(255,179,71,0.08)',
    icon: '⚠',
    message: 'Elevated physiological stress detected. Increased vigilance advised.',
  },
  HIGH: {
    color: '#ff4d6d',
    glow: 'rgba(255,77,109,0.6)',
    bg: 'rgba(255,77,109,0.1)',
    icon: '!',
    message: 'Critical distress indicators present. Immediate clinical review required.',
  },
};

export default function DistressMeter({ score = 0, riskLevel = 'LOW', triggeredRules = [] }) {
  const cfg = LEVEL_CONFIG[riskLevel] || LEVEL_CONFIG.LOW;
  const pct = Math.round(score * 100);

  return (
    <div
      className="distress-meter"
      style={{
        '--dm-color': cfg.color,
        '--dm-glow': cfg.glow,
        background: cfg.bg,
        borderColor: cfg.color,
      }}
    >
      <div className="distress-meter__top">
        <div className="distress-meter__label">Distress Score</div>
        <div
          className="distress-meter__badge"
          style={{ color: cfg.color, borderColor: cfg.color, boxShadow: `0 0 12px ${cfg.glow}` }}
        >
          <span className="distress-meter__badge-icon">{cfg.icon}</span>
          {riskLevel}
        </div>
      </div>

      <div className="distress-meter__score" style={{ color: cfg.color }}>
        {pct}
        <span className="distress-meter__score-unit">/ 100</span>
      </div>

      {/* Progress bar */}
      <div className="distress-meter__bar-track">
        <div
          className="distress-meter__bar-fill"
          style={{
            width: `${pct}%`,
            background: `linear-gradient(90deg, ${cfg.color}88, ${cfg.color})`,
            boxShadow: `0 0 10px ${cfg.glow}`,
          }}
        />
        {/* Threshold markers */}
        <div className="distress-meter__marker" style={{ left: '30%' }} title="MODERATE threshold" />
        <div className="distress-meter__marker" style={{ left: '70%' }} title="HIGH threshold" />
      </div>
      <div className="distress-meter__scale">
        <span style={{ color: '#a8ff78' }}>LOW</span>
        <span style={{ color: '#ffb347' }}>MODERATE</span>
        <span style={{ color: '#ff4d6d' }}>HIGH</span>
      </div>

      <p className="distress-meter__message" style={{ color: cfg.color }}>
        {cfg.message}
      </p>

      {triggeredRules.length > 0 && (
        <ul className="distress-meter__rules">
          {triggeredRules.map((rule, i) => (
            <li key={i} style={{ color: cfg.color }}>
              ▸ {rule}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
