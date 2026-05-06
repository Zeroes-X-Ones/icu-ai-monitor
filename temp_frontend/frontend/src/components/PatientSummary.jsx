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

  // Refresh summary every 10 seconds
  useEffect(() => {
    fetchSummary();
    const interval = setInterval(fetchSummary, 10_000);
    return () => clearInterval(interval);
  }, []);

  const borderColor =
    riskLevel === 'HIGH' ? '#ff4d6d' : riskLevel === 'MODERATE' ? '#ffb347' : '#00d4ff';

  return (
    <div className="patient-summary" style={{ borderColor }}>
      <div className="patient-summary__header">
        <span className="patient-summary__icon">⬡</span>
        <span className="patient-summary__title">AI Clinical Summary</span>
        <button
          className="patient-summary__refresh"
          onClick={fetchSummary}
          disabled={loading}
          style={{ color: borderColor, borderColor }}
        >
          {loading ? '⟳ Analyzing…' : '↻ Refresh'}
        </button>
      </div>

      <div className={`patient-summary__body ${loading ? 'loading' : ''}`}>
        <p>{summary}</p>
      </div>

      {lastUpdated && (
        <div className="patient-summary__footer">
          Last updated: {lastUpdated}
        </div>
      )}
    </div>
  );
}
