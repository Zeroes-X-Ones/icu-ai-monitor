import { useEffect, useRef, useState } from 'react';
import { API } from '../services/api';
import VitalCard from '../components/VitalCard';
import TrendChart from '../components/TrendChart';
import DistressMeter from '../components/DistressMeter';
import PatientSummary from '../components/PatientSummary';

const INITIAL_VITALS = { heart_rate: null, spo2: null, respiratory_rate: null };

export default function Dashboard() {
  const [vitals, setVitals] = useState(INITIAL_VITALS);
  const [distress, setDistress] = useState({ distress_score: 0, risk_level: 'LOW', triggered_rules: [] });
  const [history, setHistory] = useState([]);
  const [trends, setTrends] = useState({});
  const [connected, setConnected] = useState(false);
  const [tick, setTick] = useState(0);
  const wsRef = useRef(null);
  const reconnectRef = useRef(null);

  const connect = () => {
    wsRef.current = API.createWebSocket(
      (data) => {
        if (data.vitals) setVitals({ ...data.vitals });
        if (data.distress) setDistress({ ...data.distress });
        if (data.history) setHistory([...data.history]);
        if (data.trends) setTrends({ ...data.trends });
        setConnected(true);
        setTick((t) => t + 1);
      },
      () => {
        setConnected(false);
        scheduleReconnect();
      }
    );

    wsRef.current.onclose = () => {
      setConnected(false);
      scheduleReconnect();
    };
  };

  const scheduleReconnect = () => {
    clearTimeout(reconnectRef.current);
    reconnectRef.current = setTimeout(connect, 3000);
  };

  useEffect(() => {
    connect();
    return () => {
      wsRef.current?.close();
      clearTimeout(reconnectRef.current);
    };
  }, []);

  const now = new Date().toLocaleTimeString();

  return (
    <div className="dashboard">
      {/* Header */}
      <header className="dashboard__header">
        <div className="dashboard__logo">
          <span className="dashboard__logo-icon">⬡</span>
          <div>
            <div className="dashboard__logo-title">ICU AI MONITOR</div>
            <div className="dashboard__logo-sub">Physiological Surveillance System v1.0</div>
          </div>
        </div>
        <div className="dashboard__status-bar">
          <span className="dashboard__patient">Patient: BED-04 · ICU Ward A</span>
          <span
            className="dashboard__conn"
            style={{ color: connected ? '#a8ff78' : '#ff4d6d' }}
          >
            <span
              className={`dashboard__conn-dot ${connected ? 'pulse' : ''}`}
              style={{ background: connected ? '#a8ff78' : '#ff4d6d' }}
            />
            {connected ? 'LIVE' : 'RECONNECTING…'}
          </span>
          <span className="dashboard__time">{now}</span>
        </div>
      </header>

      {/* Vital Cards */}
      <section className="dashboard__vitals">
        {['heart_rate', 'spo2', 'respiratory_rate'].map((sig) => (
          <VitalCard
            key={sig}
            signal={sig}
            value={vitals[sig]}
            trend={trends[sig]}
          />
        ))}
      </section>

      {/* Charts */}
      <section className="dashboard__charts">
        {['heart_rate', 'spo2', 'respiratory_rate'].map((sig) => (
          <TrendChart key={sig} signal={sig} history={history} />
        ))}
      </section>

      {/* Bottom row: distress + summary */}
      <section className="dashboard__bottom">
        <DistressMeter
          score={distress.distress_score}
          riskLevel={distress.risk_level}
          triggeredRules={distress.triggered_rules}
        />
        <PatientSummary riskLevel={distress.risk_level} />
      </section>

      {/* Footer */}
      <footer className="dashboard__footer">
        ⚠ FOR DEMONSTRATION PURPOSES ONLY — NOT FOR CLINICAL USE &nbsp;|&nbsp; ICU-AI-MONITOR Phase 1
      </footer>
    </div>
  );
}
