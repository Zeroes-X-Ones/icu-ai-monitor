import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceArea, Legend } from 'recharts';

export default function MainChart({ data, filter }) {
  if (!data || data.length === 0) return <div className="h-full w-full flex items-center justify-center text-slate-400 absolute inset-0">Connecting to ICU Monitor stream...</div>;

  const formatDate = (tickItem) => {
    const d = new Date(tickItem);
    return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
  };

  const showHR = !filter || filter === 'heart_rate';
  const showSpO2 = !filter || filter === 'spo2';
  const showBP = !filter || filter === 'bp';

  return (
    <ResponsiveContainer width="100%" height="100%" className="absolute inset-0">
      <LineChart data={data} margin={{ top: 15, right: 20, left: -20, bottom: 5 }}>
        <CartesianGrid strokeDasharray="4 4" vertical={false} stroke="#f1f5f9" />
        <XAxis 
          dataKey="timestamp" 
          tickFormatter={formatDate} 
          minTickGap={60}
          tick={{ fontSize: 12, fill: '#94a3b8', fontWeight: 500 }}
          axisLine={false}
          tickLine={false}
          dy={10}
        />
        
        {/* Y Axis mappings based on what is shown */}
        {showHR && (
          <YAxis 
            yAxisId="hr" 
            domain={[40, 160]} 
            tick={{ fontSize: 12, fill: '#94a3b8', fontWeight: 500 }}
            axisLine={false}
            tickLine={false}
          />
        )}
        
        {showSpO2 && (
          <YAxis 
            yAxisId="spo2" 
            orientation={showHR ? "right" : "left"} 
            domain={[70, 110]} 
            tick={{ fontSize: 12, fill: '#94a3b8', fontWeight: 500 }}
            axisLine={false}
            tickLine={false}
          />
        )}

        {showBP && (
          <YAxis 
            yAxisId="bp" 
            orientation={showSpO2 || showHR ? "right" : "left"} 
            domain={[40, 220]} 
            tick={{ fontSize: 12, fill: '#94a3b8', fontWeight: 500 }}
            axisLine={false}
            tickLine={false}
          />
        )}

        <Tooltip 
          labelFormatter={(lbl) => new Date(lbl).toLocaleTimeString()}
          contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 10px 25px -5px rgb(0 0 0 / 0.1)', padding: '12px' }}
          itemStyle={{ fontWeight: 600 }}
        />
        
        <Legend verticalAlign="top" height={40} iconType="circle" wrapperStyle={{ paddingTop: "0px", paddingBottom: "10px", fontSize: "14px", fontWeight: "500", color: "#475569" }}/>
        
        {/* Critical Zones */}
        {showHR && <ReferenceArea yAxisId="hr" y1={120} y2={160} fill="#ffe4e6" fillOpacity={0.6} />}
        {showSpO2 && <ReferenceArea yAxisId="spo2" y1={70} y2={90} fill="#e0f2fe" fillOpacity={0.6} />}

        {/* Lines */}
        {showHR && (
          <Line 
            yAxisId="hr"
            type="monotone" 
            dataKey="heart_rate" 
            stroke="#f43f5e" 
            strokeWidth={3}
            dot={false}
            activeDot={{ r: 7, fill: '#f43f5e', stroke: '#fff', strokeWidth: 2 }}
            name="Heart Rate (BPM)"
            isAnimationActive={false}
          />
        )}

        {showSpO2 && (
          <Line 
            yAxisId="spo2"
            type="monotone" 
            dataKey="spo2" 
            stroke="#0ea5e9" 
            strokeWidth={3}
            dot={false}
            activeDot={{ r: 7, fill: '#0ea5e9', stroke: '#fff', strokeWidth: 2 }}
            name="SpO₂ (%)"
            isAnimationActive={false}
          />
        )}

        {showBP && (
          <>
            <Line 
              yAxisId="bp"
              type="monotone" 
              dataKey="blood_pressure_systolic" 
              stroke="#8b5cf6" 
              strokeWidth={3}
              dot={false}
              activeDot={{ r: 7, fill: '#8b5cf6', stroke: '#fff', strokeWidth: 2 }}
              name="BP Systolic (mmHg)"
              isAnimationActive={false}
            />
            <Line 
              yAxisId="bp"
              type="monotone" 
              dataKey="blood_pressure_diastolic" 
              stroke="#a78bfa" 
              strokeWidth={3}
              dot={false}
              strokeDasharray="5 5"
              activeDot={{ r: 7, fill: '#a78bfa', stroke: '#fff', strokeWidth: 2 }}
              name="BP Diastolic (mmHg)"
              isAnimationActive={false}
            />
          </>
        )}

      </LineChart>
    </ResponsiveContainer>
  );
}
