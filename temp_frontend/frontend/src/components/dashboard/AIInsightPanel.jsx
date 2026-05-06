import React, { useState, useEffect } from 'react';
import { Activity, AlertTriangle, CheckCircle2, TrendingDown, TrendingUp, Minus } from 'lucide-react';

export default function AIInsightPanel({ metric }) {
  const [windowMin, setWindowMin] = useState(15);
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchAnalysis = async () => {
      setLoading(true);
      try {
        const url = metric 
            ? `http://localhost:8000/api/v1/analysis/?window=${windowMin}&metric=${metric}`
            : `http://localhost:8000/api/v1/analysis/?window=${windowMin}`;
        const res = await fetch(url);
        const data = await res.json();
        setAnalysis(data);
      } catch (err) {
        console.error(err);
      }
      setLoading(false);
    };
    
    fetchAnalysis();
    const interval = setInterval(fetchAnalysis, 30000); 
    return () => clearInterval(interval);
  }, [windowMin, metric]);

  const getTrendIcon = (t) => {
    if (t === 'increasing' || t === 'worsening') return <TrendingUp size={14} />;
    if (t === 'decreasing') return <TrendingDown size={14} />;
    return <Minus size={14} />;
  };

  return (
    <div className="bg-white rounded-[24px] p-8 shadow-[0_2px_14px_-6px_rgba(0,0,0,0.06)] h-full flex flex-col min-h-[360px]">
      
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <h3 className="font-serif text-[#1e1a17] text-[19px]">Intelligent Analysis</h3>
          {analysis && analysis.risk_level && (
            <span className={`px-2.5 py-1 text-[10px] font-bold uppercase tracking-wider rounded-full flex items-center gap-1.5 ${
              analysis.risk_level === 'CRITICAL' ? 'bg-red-100 text-red-700' :
              analysis.risk_level === 'WARNING' ? 'bg-orange-100 text-orange-700' :
              'bg-emerald-100 text-emerald-700'
            }`}>
              {analysis.risk_level === 'CRITICAL' ? <AlertTriangle size={12} /> : 
               analysis.risk_level === 'WARNING' ? <Activity size={12} /> : 
               <CheckCircle2 size={12} />}
              {analysis.risk_level}
            </span>
          )}
        </div>
        
        <div className="flex gap-4">
          {[15, 30, 45].map((w) => (
             <button
               key={w}
               onClick={() => setWindowMin(w)}
               className={`text-[11px] font-semibold tracking-wider transition-colors ${windowMin === w ? 'text-[#b46b41]' : 'text-[#a2998d] hover:text-[#1e1a17]'}`}
             >
               {w} Min
             </button>
          ))}
        </div>
      </div>

      <div className="flex-1 flex flex-col justify-center h-full">
        {loading && !analysis ? (
          <p className="text-sm text-[#8c8273] text-center w-full">Generating intelligent insights...</p>
        ) : analysis ? (
          <div className="w-full flex flex-col gap-5">
            
            <div className="grid grid-cols-1 gap-4">
              <div className="bg-slate-50 rounded-xl p-4 border border-slate-100">
                <h4 className="text-[10px] uppercase tracking-wider font-bold text-slate-400 mb-1.5">Key Observation</h4>
                <p className="text-[13px] font-medium text-slate-800 leading-relaxed">
                  {analysis.key_observation || "Insufficient data for detailed observation."}
                </p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="bg-slate-50 rounded-xl p-4 border border-slate-100">
                  <h4 className="text-[10px] uppercase tracking-wider font-bold text-slate-400 mb-1.5">Possible Cause</h4>
                  <p className="text-[12px] text-slate-700 leading-snug">
                    {analysis.possible_cause || "N/A"}
                  </p>
                </div>
                
                <div className="bg-slate-50 rounded-xl p-4 border border-slate-100">
                  <h4 className="text-[10px] uppercase tracking-wider font-bold text-slate-400 mb-1.5">Prediction</h4>
                  <p className="text-[12px] text-slate-700 leading-snug">
                    {analysis.prediction || "N/A"}
                  </p>
                </div>
              </div>
            </div>

            <div className="flex items-center justify-between px-2 pt-2 border-t border-slate-100">
              <div className="flex items-center gap-2">
                <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Confidence Score:</span>
                <span className={`text-[12px] font-bold ${analysis.confidence_score > 0.7 ? 'text-emerald-600' : analysis.confidence_score > 0.4 ? 'text-orange-500' : 'text-slate-500'}`}>
                  {Math.round((analysis.confidence_score || 0) * 100)}%
                </span>
              </div>

              <div className="flex items-center gap-4">
                {metric && analysis.metrics && analysis.metrics[metric] ? (
                  <div className="flex items-center gap-3 text-[11px] uppercase font-bold tracking-wider text-slate-500">
                    <span>Avg: <span className="text-slate-800">{Math.round(analysis.metrics[metric].avg)}</span></span>
                    <span className="flex items-center gap-1">
                      Trend: 
                      <span className={`flex items-center gap-0.5 ${
                        analysis.metrics[metric].trend === 'stable' ? 'text-slate-800' : 
                        ((metric === 'spo2' && analysis.metrics[metric].trend === 'decreasing') || 
                        ((metric === 'heart_rate' || metric === 'bp') && analysis.metrics[metric].trend === 'increasing'))
                        ? 'text-orange-500' : 'text-green-600'
                      }`}>
                        {analysis.metrics[metric].trend} {getTrendIcon(analysis.metrics[metric].trend)}
                      </span>
                    </span>
                  </div>
                ) : (
                  <div className="flex items-center gap-1 text-[11px] uppercase font-bold tracking-wider text-slate-500">
                     Overall Trend: 
                     <span className={`flex items-center gap-0.5 ml-1 ${analysis.trend === 'worsening' ? 'text-orange-500' : analysis.trend === 'improving' ? 'text-green-600' : 'text-slate-800'}`}>
                        {analysis.trend} {getTrendIcon(analysis.trend)}
                     </span>
                  </div>
                )}
              </div>
            </div>
            
          </div>
        ) : (
           <p className="text-sm text-[#8c8273] text-center w-full">No analysis available.</p>
        )}
      </div>
      
    </div>
  );
}
