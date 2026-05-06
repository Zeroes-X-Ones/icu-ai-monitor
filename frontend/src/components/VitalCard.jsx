// import { useEffect, useRef } from 'react';

// const SIGNAL_CONFIG = {
//   heart_rate: {
//     label: 'Heart Rate',
//     unit: 'bpm',
//     icon: '♥',
//     normal: [60, 100],
//     color: '#ff4d6d',
//     glowColor: 'rgba(255,77,109,0.4)',
//   },
//   spo2: {
//     label: 'SpO₂',
//     unit: '%',
//     icon: '◎',
//     normal: [94, 100],
//     color: '#00d4ff',
//     glowColor: 'rgba(0,212,255,0.4)',
//   },
//   respiratory_rate: {
//     label: 'Resp. Rate',
//     unit: 'br/min',
//     icon: '~',
//     normal: [12, 24],
//     color: '#a8ff78',
//     glowColor: 'rgba(168,255,120,0.4)',
//   },
// };

// export default function VitalCard({ signal, value, trend }) {
//   const cfg = SIGNAL_CONFIG[signal];
//   const prevRef = useRef(value);
//   const cardRef = useRef(null);

//   const isNormal =
//     value >= cfg.normal[0] && value <= cfg.normal[1];

//   // Flash animation on value change
//   useEffect(() => {
//     if (value !== prevRef.current && cardRef.current) {
//       cardRef.current.classList.add('flash');
//       setTimeout(() => cardRef.current?.classList.remove('flash'), 300);
//       prevRef.current = value;
//     }
//   }, [value]);

//   const statusDot = isNormal ? '#a8ff78' : '#ff4d6d';
//   const statusText = isNormal ? 'NORMAL' : 'ALERT';

//   return (
//     <div
//       ref={cardRef}
//       className="vital-card"
//       style={{
//         '--card-color': cfg.color,
//         '--card-glow': cfg.glowColor,
//       }}
//     >
//       <div className="vital-card__header">
//         <span className="vital-card__icon" style={{ color: cfg.color }}>
//           {cfg.icon}
//         </span>
//         <span className="vital-card__label">{cfg.label}</span>
//         <span
//           className="vital-card__status"
//           style={{ color: statusDot, borderColor: statusDot }}
//         >
//           {statusText}
//         </span>
//       </div>

//       <div className="vital-card__value" style={{ color: cfg.color }}>
//         {value !== null && value !== undefined ? (
//           <>
//             <span className="vital-card__number">
//               {typeof value === 'number' ? value.toFixed(1) : value}
//             </span>
//             <span className="vital-card__unit">{cfg.unit}</span>
//           </>
//         ) : (
//           <span className="vital-card__loading">---</span>
//         )}
//       </div>

//       {trend && (
//         <div
//           className="vital-card__trend"
//           style={{
//             color:
//               trend.direction === 'stable'
//                 ? '#888'
//                 : trend.direction === 'rising'
//                   ? '#ffb347'
//                   : '#00d4ff',
//           }}
//         >
//           {trend.direction === 'rising' ? '▲' : trend.direction === 'falling' ? '▼' : '—'}{' '}
//           {trend.label}
//         </div>
//       )}

//       <div
//         className="vital-card__bar"
//         style={{
//           background: `linear-gradient(90deg, ${cfg.color} ${isNormal ? 70 : 35}%, transparent)`,
//         }}
//       />
//     </div>
//   );
// }


import { useEffect, useRef } from 'react';

const SIGNAL_CONFIG = {
  heart_rate: {
    label: 'Heart Rate',
    unit: 'bpm',
    color: '#ef4444',
    normal: [60, 100],
  },
  spo2: {
    label: 'SpO₂',
    unit: '%',
    color: '#3b82f6',
    normal: [94, 100],
  },
  respiratory_rate: {
    label: 'Resp. Rate',
    unit: 'br/min',
    color: '#22c55e',
    normal: [12, 24],
  },
};

export default function VitalCard({ signal, value }) {
  const cfg = SIGNAL_CONFIG[signal];
  const prevRef = useRef(value);
  const ref = useRef(null);

  const isNormal =
    value >= cfg.normal[0] && value <= cfg.normal[1];

  useEffect(() => {
    if (value !== prevRef.current && ref.current) {
      ref.current.classList.add('animate-pulse');
      setTimeout(() => ref.current?.classList.remove('animate-pulse'), 300);
      prevRef.current = value;
    }
  }, [value]);

  return (
    <div
      ref={ref}
      className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm"
    >
      <div className="flex justify-between items-center mb-2">
        <span className="text-sm text-slate-500">{cfg.label}</span>
        <span
          className={`text-xs font-bold px-2 py-1 rounded-full ${isNormal
            ? 'bg-green-100 text-green-700'
            : 'bg-red-100 text-red-700'
            }`}
        >
          {isNormal ? 'NORMAL' : 'ALERT'}
        </span>
      </div>

      <div className="flex items-end gap-2">
        <span
          className="text-3xl font-bold"
          style={{ color: cfg.color }}
        >
          {value}
        </span>
        <span className="text-xs text-slate-400">
          {cfg.unit}
        </span>
      </div>
    </div>
  );
}
