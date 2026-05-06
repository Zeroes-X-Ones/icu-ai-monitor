import { useEffect, useRef } from 'react';

const SIGNAL_CONFIG = {
  heart_rate: {
    label: 'Heart Rate',
    unit: 'bpm',
    icon: '♥',
    normal: [60, 100],
    color: '#ff4d6d',
    glowColor: 'rgba(255,77,109,0.4)',
  },
  spo2: {
    label: 'SpO₂',
    unit: '%',
    icon: '◎',
    normal: [94, 100],
    color: '#00d4ff',
    glowColor: 'rgba(0,212,255,0.4)',
  },
  respiratory_rate: {
    label: 'Resp. Rate',
    unit: 'br/min',
    icon: '~',
    normal: [12, 24],
    color: '#a8ff78',
    glowColor: 'rgba(168,255,120,0.4)',
  },
};

export default function VitalCard({ signal, value, trend }) {
  const cfg = SIGNAL_CONFIG[signal];
  const prevRef = useRef(value);
  const cardRef = useRef(null);

  const isNormal =
    value >= cfg.normal[0] && value <= cfg.normal[1];

  // Flash animation on value change
  useEffect(() => {
    if (value !== prevRef.current && cardRef.current) {
      cardRef.current.classList.add('flash');
      setTimeout(() => cardRef.current?.classList.remove('flash'), 300);
      prevRef.current = value;
    }
  }, [value]);

  const statusDot = isNormal ? '#a8ff78' : '#ff4d6d';
  const statusText = isNormal ? 'NORMAL' : 'ALERT';

  return (
    <div
      ref={cardRef}
      className="vital-card"
      style={{
        '--card-color': cfg.color,
        '--card-glow': cfg.glowColor,
      }}
    >
      <div className="vital-card__header">
        <span className="vital-card__icon" style={{ color: cfg.color }}>
          {cfg.icon}
        </span>
        <span className="vital-card__label">{cfg.label}</span>
        <span
          className="vital-card__status"
          style={{ color: statusDot, borderColor: statusDot }}
        >
          {statusText}
        </span>
      </div>

      <div className="vital-card__value" style={{ color: cfg.color }}>
        {value !== null && value !== undefined ? (
          <>
            <span className="vital-card__number">
              {typeof value === 'number' ? value.toFixed(1) : value}
            </span>
            <span className="vital-card__unit">{cfg.unit}</span>
          </>
        ) : (
          <span className="vital-card__loading">---</span>
        )}
      </div>

      {trend && (
        <div
          className="vital-card__trend"
          style={{
            color:
              trend.direction === 'stable'
                ? '#888'
                : trend.direction === 'rising'
                ? '#ffb347'
                : '#00d4ff',
          }}
        >
          {trend.direction === 'rising' ? '▲' : trend.direction === 'falling' ? '▼' : '—'}{' '}
          {trend.label}
        </div>
      )}

      <div
        className="vital-card__bar"
        style={{
          background: `linear-gradient(90deg, ${cfg.color} ${isNormal ? 70 : 35}%, transparent)`,
        }}
      />
    </div>
  );
}
