import React, { useState, useEffect, useMemo } from 'react';
import { Clock, Filter, ArrowDown, ArrowUp, Activity, AlertTriangle, CheckCircle2, ChevronDown, ChevronUp, ChevronRight, AlertCircle, Download } from 'lucide-react';
import { downloadCSV } from '../../utils/csvExport';

export default function HistoryView() {
  const [minutes, setMinutes] = useState(60);
  const [vitals, setVitals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [sortAsc, setSortAsc] = useState(false);
  const [expandedRows, setExpandedRows] = useState(new Set());
  const [sessionStart, setSessionStart] = useState(null);
  const [showOnlyAbnormal, setShowOnlyAbnormal] = useState(false);
  const formatTime = (ts) => {
    const date = new Date(ts);

    return date.toLocaleString('en-IN', {
      timeZone: 'Asia/Kolkata',
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  };

  useEffect(() => {
    const fetchHistory = async () => {
      setLoading(true);
      try {
        const res = await fetch(`https://icu-ai-monitor-d6z0.onrender.com/api/v1/vitals/history?minutes=${minutes}`);
        const data = await res.json();
        setVitals(data.history || []);
        // const res = await fetch(`http://localhost:8000/api/v1/vitals/?minutes=${minutes}`);
        // const data = await res.json();
        // setVitals(data);
      } catch (err) {
        console.error(err);
      }
      setLoading(false);
    };
    fetchHistory();
    const interval = setInterval(fetchHistory, 60000);
    return () => clearInterval(interval);
  }, [minutes]);

  //added 
  useEffect(() => {
    const fetchSession = async () => {
      try {
        const res = await fetch("https://icu-ai-monitor-d6z0.onrender.com");
        const data = await res.json();
        setSessionStart(data.start);
      } catch (err) {
        console.error(err);
      }
    };

    fetchSession();
  }, []);

  const { processedData, extremes, summaryStats } = useMemo(() => {
    if (!vitals.length) return { processedData: [], extremes: {}, summaryStats: {} };

    let maxHR = -Infinity, maxBP = -Infinity, minSpO2 = Infinity;
    let totalHRSpikes = 0, totalSpO2Drops = 0, totalBPSpikes = 0;

    vitals.forEach(v => {
      if (v.heart_rate > maxHR) maxHR = v.heart_rate;
      if (v.blood_pressure_systolic > maxBP) maxBP = v.blood_pressure_systolic;
      if (v.spo2 < minSpO2) minSpO2 = v.spo2;

      if (v.heart_rate > 100 || v.heart_rate < 60) totalHRSpikes++;
      if (v.spo2 < 94) totalSpO2Drops++;
      if (v.blood_pressure_systolic > 130) totalBPSpikes++;
    });

    const processed = vitals.map((vital, i, arr) => {
      let sumHR = 0, sumSpO2 = 0, sumBP = 0, count = 0;
      let localMinHR = vital.heart_rate, localMaxHR = vital.heart_rate;

      for (let j = 1; j <= 5; j++) {
        if (i + j < arr.length) {
          sumHR += arr[i + j].heart_rate;
          sumSpO2 += arr[i + j].spo2;
          sumBP += arr[i + j].blood_pressure_systolic;

          if (arr[i + j].heart_rate < localMinHR) localMinHR = arr[i + j].heart_rate;
          if (arr[i + j].heart_rate > localMaxHR) localMaxHR = arr[i + j].heart_rate;

          count++;
        }
      }

      let trend = 'stable';
      if (count > 0) {
        const avgHR = sumHR / count;
        const avgSpO2 = sumSpO2 / count;
        const avgBP = sumBP / count;

        if (vital.heart_rate - avgHR > 5 || vital.blood_pressure_systolic - avgBP > 10) trend = 'increasing';
        else if (vital.heart_rate - avgHR < -5 || vital.blood_pressure_systolic - avgBP < -10) trend = 'decreasing';
        if (vital.spo2 - avgSpO2 < -1.5) trend = 'worsening';
      }

      // Generate dynamic summary
      let dynamicSummary = "";
      let eventType = "Normal";

      if (vital.alert_level === 'CRITICAL') {
        eventType = "🔴 Critical";
        dynamicSummary = `Critical event detected. Heart rate at ${Math.round(vital.heart_rate)} bpm and SpO2 at ${Math.round(vital.spo2)}%. Immediate attention recommended.`;
      } else if (vital.alert_level === 'WARNING') {
        eventType = "🟡 Warning";
        if (vital.heart_rate > 100) {
          eventType = "⚠️ Spike";
          dynamicSummary = `Heart rate spike detected (${Math.round(vital.heart_rate)} bpm). Monitor for sustained tachycardia.`;
        } else if (vital.spo2 < 94) {
          eventType = "⚠️ Drop";
          dynamicSummary = `Oxygen desaturation detected (${Math.round(vital.spo2)}%). Assess airway and respiratory effort.`;
        } else {
          dynamicSummary = `Abnormal vital pattern observed. HR: ${Math.round(vital.heart_rate)} bpm, BP: ${vital.blood_pressure_systolic} mmHg.`;
        }
      } else {
        dynamicSummary = `Heart rate within normal range (${Math.round(localMinHR)}–${Math.round(localMaxHR)} bpm). No abnormal variation detected in SpO2 (${Math.round(vital.spo2)}%).`;
      }

      return { ...vital, calculatedTrend: trend, dynamicSummary, eventType };
    });

    let filtered = processed;
    if (showOnlyAbnormal) {
      filtered = processed.filter(r => r.alert_level === 'WARNING' || r.alert_level === 'CRITICAL');
    }

    if (sortAsc) {
      filtered = [...filtered].reverse();
    }

    return {
      processedData: filtered,
      extremes: { maxHR, maxBP, minSpO2 },
      summaryStats: { totalHRSpikes, totalSpO2Drops, totalBPSpikes }
    };
  }, [vitals, sortAsc, showOnlyAbnormal]);

  const toggleRow = (id) => {
    const newExpanded = new Set(expandedRows);
    if (newExpanded.has(id)) newExpanded.delete(id);
    else newExpanded.add(id);
    setExpandedRows(newExpanded);
  };

  const handleDownloadCSV = () => {
    const csvData = processedData.map(row => ({
      timestamp: new Date(row.timestamp).toISOString(),
      HR: Math.round(row.heart_rate),
      SpO2: Math.round(row.spo2),
      BP: `${Math.round(row.blood_pressure_systolic)}/${Math.round(row.blood_pressure_diastolic)}`,
      status: row.alert_level === 'INFO' ? 'NORMAL' : row.alert_level
    }));
    downloadCSV(csvData, `vitals_history_${minutes}min.csv`);
  };

  const getStatusBadge = (level) => {
    switch (level) {
      case 'CRITICAL': return <span className="px-3 py-1 text-xs font-bold bg-red-100 text-red-700 rounded-full flex items-center justify-center gap-1 w-max mx-auto"><AlertTriangle size={14} /> CRITICAL</span>;
      case 'WARNING': return <span className="px-3 py-1 text-xs font-bold bg-yellow-100 text-yellow-700 rounded-full flex items-center justify-center gap-1 w-max mx-auto"><Activity size={14} /> WARNING</span>;
      default: return <span className="px-3 py-1 text-xs font-bold bg-green-100 text-green-700 rounded-full flex items-center justify-center gap-1 w-max mx-auto"><CheckCircle2 size={14} /> NORMAL</span>;
    }
  };

  const getTrendIcon = (t) => {
    if (t === 'increasing') return <ArrowUp size={16} className="text-yellow-500 mx-auto" />;
    if (t === 'decreasing' || t === 'worsening') return <ArrowDown size={16} className={`${t === 'worsening' ? 'text-yellow-500' : 'text-green-500'} mx-auto`} />;
    return <span className="text-slate-400 font-bold px-1 flex justify-center">→</span>;
  };

  return (
    <div className="h-full flex flex-col p-8 gap-6">

      <div className="flex items-center justify-between shrink-0">
        <div>
          <h2 className="text-[24px] font-serif text-[#1e1a17] tracking-tight">Vitals History</h2>
          {sessionStart && (
            <p className="text-[12px] text-slate-400 mt-1">
              Monitoring started at:{" "}
              {new Date(sessionStart).toLocaleTimeString('en-IN', {
                timeZone: 'Asia/Kolkata'
              })}
            </p>
          )}
          <p className="text-[13px] text-[#8c8273] mt-1">Full historical log with dynamic event detection.</p>
        </div>

        <div className="flex items-center gap-4">
          <label className="flex items-center gap-2 text-[13px] font-medium text-slate-600 cursor-pointer bg-white px-4 py-2 rounded-lg border border-slate-200 transition-colors hover:bg-slate-50">
            <input
              type="checkbox"
              checked={showOnlyAbnormal}
              onChange={(e) => setShowOnlyAbnormal(e.target.checked)}
              className="rounded text-blue-600 focus:ring-blue-500 border-slate-300"
            />
            Show Abnormal Only
          </label>

          <div className="flex items-center gap-2">
            {[15, 60, 300].map((w) => (
              <button
                key={w}
                onClick={() => setMinutes(w)}
                className={`px-3 py-1 text-[13px] font-medium rounded-md transition-colors ${minutes === w ? 'bg-blue-500 text-white' : 'bg-slate-200 text-slate-700 hover:bg-slate-300'
                  }`}
              >
                {w === 60 ? '1 Hour' : w === 300 ? '5 Hours' : '15 Min'}
              </button>
            ))}
          </div>

          <button
            onClick={() => setSortAsc(!sortAsc)}
            className="flex items-center gap-2 text-[13px] font-medium bg-white px-4 py-2 rounded-lg border border-slate-200 text-slate-600 hover:bg-slate-50 transition-colors"
          >
            <Filter size={14} />
            {sortAsc ? 'Oldest First' : 'Newest First'}
          </button>

          <button
            onClick={handleDownloadCSV}
            className="flex items-center gap-2 text-[13px] font-medium bg-slate-900 text-white px-4 py-2 rounded-lg hover:bg-slate-800 transition-colors"
          >
            <Download size={14} />
            Download CSV
          </button>
        </div>
      </div>

      {!loading && vitals.length > 0 && (
        <div className="grid grid-cols-3 gap-4 shrink-0">
          <div className="bg-white p-4 rounded-xl border border-slate-200 flex items-center gap-4">
            <div className="w-10 h-10 rounded-full bg-yellow-100 flex items-center justify-center text-yellow-600"><Activity size={20} /></div>
            <div>
              <p className="text-[11px] font-bold uppercase tracking-wider text-slate-500">Heart Rate Spikes</p>
              <p className="text-[18px] font-semibold text-slate-900">{summaryStats.totalHRSpikes}</p>
            </div>
          </div>
          <div className="bg-white p-4 rounded-xl border border-slate-200 flex items-center gap-4">
            <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center text-blue-600"><AlertCircle size={20} /></div>
            <div>
              <p className="text-[11px] font-bold uppercase tracking-wider text-slate-500">Oxygen Drops</p>
              <p className="text-[18px] font-semibold text-slate-900">{summaryStats.totalSpO2Drops}</p>
            </div>
          </div>
          <div className="bg-white p-4 rounded-xl border border-slate-200 flex items-center gap-4">
            <div className="w-10 h-10 rounded-full bg-green-100 flex items-center justify-center text-green-600"><CheckCircle2 size={20} /></div>
            <div>
              <p className="text-[11px] font-bold uppercase tracking-wider text-slate-500">Overall Condition</p>
              <p className="text-[14px] font-semibold text-slate-900 mt-0.5">
                {summaryStats.totalHRSpikes + summaryStats.totalSpO2Drops > 5 ? 'Unstable / Needs Review' : 'Stable'}
              </p>
            </div>
          </div>
        </div>
      )}

      <div className="flex-1 bg-white rounded-lg border border-slate-200 p-4 flex flex-col overflow-hidden">
        {loading && !vitals.length ? (
          <div className="flex-1 flex items-center justify-center text-slate-500 font-medium">Loading history...</div>
        ) : (
          <div className="overflow-y-auto flex-1 custom-scrollbar rounded-lg border border-slate-200">
            <table className="w-full text-left text-[13px] border-collapse">
              <thead className="sticky top-0 bg-slate-100 z-10 border-b border-slate-200">
                <tr>
                  <th className="px-6 py-4 font-bold text-slate-700 uppercase tracking-wider text-xs text-left">Timestamp</th>
                  <th className="px-6 py-4 font-bold text-slate-700 uppercase tracking-wider text-xs text-left">Event</th>
                  <th className="px-6 py-4 font-bold text-slate-700 uppercase tracking-wider text-xs text-center">Heart Rate</th>
                  <th className="px-6 py-4 font-bold text-slate-700 uppercase tracking-wider text-xs text-center">SpO₂</th>
                  <th className="px-6 py-4 font-bold text-slate-700 uppercase tracking-wider text-xs text-center">BP (Sys/Dia)</th>
                  <th className="px-6 py-4 font-bold text-slate-700 uppercase tracking-wider text-xs text-center">Status</th>
                  <th className="px-6 py-4 font-bold text-slate-700 uppercase tracking-wider text-xs text-center">Trend</th>
                  <th className="px-6 py-4 w-10"></th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {processedData.map((row) => {
                  const isExpanded = expandedRows.has(row.id);
                  const isAbnormalRow = row.alert_level === 'CRITICAL' || row.alert_level === 'WARNING';
                  return (
                    <React.Fragment key={row.id}>
                      <tr
                        onClick={() => toggleRow(row.id)}
                        className={`group cursor-pointer transition-all duration-150 h-14 hover:bg-slate-100 ${isAbnormalRow
                          ? (row.alert_level === 'CRITICAL' ? 'bg-red-50' : 'bg-yellow-50')
                          : 'bg-white'
                          }`}
                      >
                        <td className="px-6 py-4 text-slate-500 font-mono text-[11px] whitespace-nowrap text-left">
                          {formatTime(row.timestamp)}

                        </td>
                        <td className="px-6 py-4 font-medium text-[13px] whitespace-nowrap text-left">
                          <span className={
                            row.eventType.includes('Critical') ? 'text-red-700 font-semibold' :
                              row.eventType.includes('Spike') || row.eventType.includes('Warning') || row.eventType.includes('Drop') ? 'text-yellow-700 font-semibold' :
                                'text-slate-600'
                          }>
                            {row.eventType}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-center">
                          <span className={`${row.heart_rate > 100 ? 'text-red-600 font-semibold' : 'text-slate-700'}`}>
                            {Math.round(row.heart_rate)}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-center">
                          <span className={`${row.spo2 < 94 ? 'text-red-600 font-semibold' : 'text-slate-700'}`}>
                            {Math.round(row.spo2)}%
                          </span>
                        </td>
                        <td className="px-6 py-4 text-center">
                          <span className={`${row.blood_pressure_systolic > 130 ? 'text-yellow-600 font-semibold' : 'text-slate-700'}`}>
                            {Math.round(row.blood_pressure_systolic)} / {Math.round(row.blood_pressure_diastolic)}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-center">
                          {getStatusBadge(row.alert_level)}
                        </td>
                        <td className="px-6 py-4 text-center">
                          {getTrendIcon(row.calculatedTrend)}
                        </td>
                        <td className="px-6 py-4 text-slate-400 text-center">
                          <ChevronRight size={16} className={`transition-transform duration-200 mx-auto ${isExpanded ? 'rotate-90' : ''}`} />
                        </td>
                      </tr>

                      {/* Expandable row */}
                      <tr>
                        <td colSpan={8} className="p-0 border-0">
                          <div
                            className={`grid transition-all duration-300 ease-in-out ${isExpanded ? 'grid-rows-[1fr] opacity-100' : 'grid-rows-[0fr] opacity-0'}`}
                          >
                            <div className={`overflow-hidden border-b ${row.alert_level === 'CRITICAL' ? 'bg-red-50/50 border-red-100' : row.alert_level === 'WARNING' ? 'bg-yellow-50/50 border-yellow-100' : 'bg-slate-50 border-slate-100'}`}>
                              <div className="p-6 flex items-start gap-4">
                                <div className="mt-0.5">
                                  {row.alert_level === 'CRITICAL' ? <AlertTriangle className="text-red-500" size={18} /> :
                                    row.alert_level === 'WARNING' ? <Activity className="text-yellow-500" size={18} /> :
                                      <CheckCircle2 className="text-green-500" size={18} />}
                                </div>
                                <div>
                                  <h4 className="text-[11px] font-bold uppercase tracking-wider text-slate-500 mb-1">Dynamic Clinical Insight</h4>
                                  <p className="text-[13px] text-slate-700 leading-relaxed">
                                    {row.dynamicSummary}
                                  </p>
                                </div>
                              </div>
                            </div>
                          </div>
                        </td>
                      </tr>
                    </React.Fragment>
                  );
                })}
                {processedData.length === 0 && !loading && (
                  <tr>
                    <td colSpan={8} className="px-6 py-12 text-center text-slate-500 font-medium">No history data found for the selected time range.</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
