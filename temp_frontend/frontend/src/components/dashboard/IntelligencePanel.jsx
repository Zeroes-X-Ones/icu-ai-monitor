import React, { useState, useEffect } from 'react';
import { useOutletContext } from 'react-router-dom';
import { AlertTriangle, Activity, CheckCircle2, ChevronRight, CheckSquare, Clock } from 'lucide-react';

export default function IntelligencePanel() {
  const { data } = useOutletContext();
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchIntelligence = async () => {
      setLoading(true);
      try {
        const res = await fetch(`http://localhost:8000/api/v1/analysis/?window=15`);
        const json = await res.json();
        setAnalysis(json);
      } catch (err) {
        console.error(err);
      }
      setLoading(false);
    };
    
    fetchIntelligence();
    const interval = setInterval(fetchIntelligence, 30000); 
    return () => clearInterval(interval);
  }, []);

  if (loading && !analysis) {
    return <div className="bg-white rounded-[24px] p-8 shadow-[0_2px_14px_-6px_rgba(0,0,0,0.06)] h-[400px] flex items-center justify-center text-slate-400">Loading Clinical Intelligence...</div>;
  }

  if (!analysis) return null;

  return (
    <div className="bg-white rounded-[24px] p-8 shadow-[0_2px_14px_-6px_rgba(0,0,0,0.06)] h-[400px] flex gap-8">
      
      {/* 1. Critical Events Panel */}
      <div className="flex-1 flex flex-col min-w-0 pr-6 border-r border-slate-100">
        <h3 className="font-serif text-[#1e1a17] text-[18px] mb-4 flex items-center gap-2">
           <AlertTriangle size={18} className="text-[#b46b41]"/> Critical Events
        </h3>
        <div className="flex-1 overflow-y-auto pr-2 custom-scrollbar flex flex-col gap-3">
          {analysis.events && analysis.events.length > 0 ? (
            analysis.events.slice(0, 5).map((e, idx) => (
               <div key={idx} className={`p-3 rounded-xl border ${e.severity === 'CRITICAL' ? 'bg-red-50 border-red-100' : 'bg-orange-50 border-orange-100'} flex items-start gap-3`}>
                  <div className={`mt-0.5 w-6 h-6 rounded-full flex items-center justify-center shrink-0 ${e.severity === 'CRITICAL' ? 'bg-red-100 text-red-600' : 'bg-orange-100 text-orange-600'}`}>
                     {e.type.includes('HR') ? <Activity size={12}/> : <AlertTriangle size={12}/>}
                  </div>
                  <div>
                    <p className="text-[10px] font-bold uppercase tracking-wider text-slate-500 mb-0.5 flex items-center gap-2">
                       {e.type.replace('_', ' ')}
                       <span className={`px-1.5 py-0.5 rounded-sm text-[8px] ${e.severity === 'CRITICAL' ? 'bg-red-600 text-white' : 'bg-orange-500 text-white'}`}>Priority: {e.priority}</span>
                    </p>
                    <p className="text-[12px] font-medium text-slate-800 leading-snug">{e.description}</p>
                    <p className="text-[10px] text-slate-400 mt-1 font-mono">{new Date(e.timestamp).toLocaleTimeString()}</p>
                  </div>
               </div>
            ))
          ) : (
             <div className="p-4 rounded-xl border border-slate-100 bg-slate-50 flex items-center gap-3">
                <CheckCircle2 size={16} className="text-emerald-500"/>
                <p className="text-[12px] text-slate-600 font-medium">No critical events detected in the current window.</p>
             </div>
          )}
        </div>
      </div>

      {/* 2. Recommendation Panel */}
      <div className="flex-1 flex flex-col min-w-0 pr-6 border-r border-slate-100">
        <h3 className="font-serif text-[#1e1a17] text-[18px] mb-4 flex items-center gap-2">
           <CheckSquare size={18} className="text-[#b46b41]"/> Recommendations
        </h3>
        <div className="flex-1 overflow-y-auto pr-2 custom-scrollbar flex flex-col gap-3">
           {analysis.recommendations && analysis.recommendations.length > 0 ? (
             analysis.recommendations.map((r, idx) => (
                <div key={idx} className="p-3 rounded-xl border border-blue-100 bg-blue-50 flex items-start gap-3">
                   <div className="mt-0.5"><ChevronRight size={16} className="text-blue-500"/></div>
                   <div>
                     <p className="text-[10px] font-bold uppercase tracking-wider text-blue-600 mb-0.5">{r.condition}</p>
                     <p className="text-[12px] font-medium text-slate-800 leading-snug">{r.action}</p>
                   </div>
                </div>
             ))
           ) : (
              <p className="text-[12px] text-slate-500">Awaiting clinical conditions to generate recommendations.</p>
           )}
        </div>
      </div>

      {/* 3. Timeline Panel */}
      <div className="flex-[0.8] flex flex-col min-w-0">
        <h3 className="font-serif text-[#1e1a17] text-[18px] mb-4 flex items-center gap-2">
           <Clock size={18} className="text-[#b46b41]"/> Timeline
        </h3>
        <div className="flex-1 overflow-y-auto pr-2 custom-scrollbar relative">
           <div className="absolute left-[7px] top-2 bottom-2 w-px bg-slate-200 z-0"></div>
           <div className="flex flex-col gap-4 relative z-10">
              {analysis.timeline && analysis.timeline.length > 0 ? (
                analysis.timeline.map((t, idx) => (
                   <div key={idx} className="flex gap-3">
                      <div className="w-3.5 h-3.5 rounded-full bg-slate-800 border-2 border-white shrink-0 mt-1 shadow-sm"></div>
                      <div>
                         <p className="text-[10px] font-bold font-mono text-slate-400 mb-0.5">{new Date(t.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</p>
                         <p className="text-[12px] font-medium text-slate-700 leading-snug">{t.event}</p>
                      </div>
                   </div>
                ))
              ) : (
                 <p className="text-[12px] text-slate-500 ml-4">Timeline building...</p>
              )}
           </div>
        </div>
      </div>
      
    </div>
  );
}
