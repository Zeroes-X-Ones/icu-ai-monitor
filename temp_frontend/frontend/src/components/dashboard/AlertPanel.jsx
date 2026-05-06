import React, { useState, useEffect } from 'react';

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

  return (
    <div className="bg-white rounded-[24px] p-8 shadow-[0_2px_14px_-6px_rgba(0,0,0,0.06)] h-full flex flex-col min-h-[300px]">
      <div className="flex justify-between items-center mb-6">
        <h3 className="font-serif text-[#1e1a17] text-[19px]">System Notifications</h3>
      </div>
      
      {explanation && (
        <div className={`mb-6 p-4 rounded-xl border ${explanation.includes('CRITICAL') ? 'bg-red-50 border-red-100 text-red-800' : explanation.includes('WARNING') ? 'bg-orange-50 border-orange-100 text-orange-800' : 'bg-slate-50 border-slate-100 text-slate-600'}`}>
           <p className="text-[10px] font-bold uppercase tracking-wider mb-1 opacity-70">Current Intelligence Status</p>
           <p className="text-[13px] font-medium leading-snug">{explanation}</p>
        </div>
      )}
      
      <div className="flex-1 overflow-y-auto pr-2 flex flex-col">
        {alerts.length === 0 ? (
          <div className="w-full text-center my-auto">
            <p className="text-[13px] text-[#8c8273]">No notifications yet.</p>
          </div>
        ) : (
          <div className="space-y-4 h-full pt-1">
            {alerts.map((alert) => (
              <div key={alert.id} className="flex gap-4 items-center border-b border-[#f0ece5] pb-3 last:border-0 last:pb-0">
                <div className={`w-2 h-2 rounded-full shrink-0 ${alert.alert_level === 'CRITICAL' ? 'bg-[#e13f28]' : 'bg-[#e0912f]'}`}></div>
                <div className="flex-1 flex justify-between items-center gap-4">
                  <p className="text-[12px] text-[#38332f] leading-snug font-medium">{alert.ai_summary}</p>
                  <p className="text-[10px] text-[#a2998d] font-semibold whitespace-nowrap">{new Date(alert.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
