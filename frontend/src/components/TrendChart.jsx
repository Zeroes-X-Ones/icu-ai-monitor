import { useEffect, useRef } from 'react';

const SIGNAL_STYLES = {
  heart_rate: {
    label: 'Heart Rate (bpm)',
    color: '#ff4d6d',
    fill: 'rgba(255,77,109,0.08)',
    yMin: 40,
    yMax: 140,
  },
  spo2: {
    label: 'SpO₂ (%)',
    color: '#00d4ff',
    fill: 'rgba(0,212,255,0.08)',
    yMin: 85,
    yMax: 102,
  },
  respiratory_rate: {
    label: 'Resp. Rate (br/min)',
    color: '#a8ff78',
    fill: 'rgba(168,255,120,0.08)',
    yMin: 8,
    yMax: 32,
  },
};

export default function TrendChart({ signal, history }) {
  const canvasRef = useRef(null);
  const chartRef = useRef(null);
  const cfg = SIGNAL_STYLES[signal];

  useEffect(() => {
    if (!canvasRef.current) return;

    let ChartJS;
    import('chart.js/auto').then((mod) => {
      ChartJS = mod.default;

      chartRef.current = new ChartJS(canvasRef.current, {
        type: 'line',
        data: {
          labels: [],
          datasets: [
            {
              label: cfg.label,
              data: [],
              borderColor: cfg.color,
              backgroundColor: cfg.fill,
              borderWidth: 2,
              pointRadius: 0,
              tension: 0.4,
              fill: true,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          animation: { duration: 300 },
          plugins: { legend: { display: false } },
          scales: {
            x: { display: false },
            y: {
              min: cfg.yMin,
              max: cfg.yMax,
              grid: { color: 'rgba(255,255,255,0.05)' },
              ticks: {
                color: '#556',
                maxTicksLimit: 5,
              },
            },
          },
        },
      });
    });

    return () => {
      chartRef.current?.destroy();
    };
  }, []);

  useEffect(() => {
    if (!chartRef.current || !history?.length) return;
    chartRef.current.data.labels = history.map((_, i) => i);
    chartRef.current.data.datasets[0].data = history.map((r) => r[signal]);
    chartRef.current.update('none');
  }, [history, signal]);

  return (
    <div className="trend-chart">
      <div className="trend-chart__title" style={{ color: cfg.color }}>
        {cfg.label}
      </div>
      <div className="trend-chart__canvas-wrap">
        <canvas ref={canvasRef} />
      </div>
    </div>
  );
}