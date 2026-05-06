import React, { useState, useEffect } from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from '../layout/Sidebar';
import { useVitalsStream } from '../../hooks/useVitalsStream';

export default function Dashboard() {
  const [history, setHistory] = useState([]);
  const [timeWindow, setTimeWindow] = useState(15);
  const [loadingHistory, setLoadingHistory] = useState(false);
  const { data, isConnected, latestVital } = useVitalsStream('wss://icu-ai-monitor-d6z0.onrender.com', history);
  
  useEffect(() => {
    setLoadingHistory(true);
    fetch(`https://icu-ai-monitor-d6z0.onrender.com/api/v1/vitals/history?minutes=${timeWindow}`)
      .then(res => res.json())
      .then(d => {
        setHistory((d.history || []).reverse());
        setLoadingHistory(false);
      })
      .catch(err => {
        console.error(err);
        setLoadingHistory(false);
      });
  }, [timeWindow]);

  return (
    <div className="flex h-screen bg-[#f5f2eb] text-[#2c2825] font-sans overflow-hidden">
      
      {/* LEFT SIDEBAR */}
      <Sidebar />

      {/* MAIN CONTENT AREA */}
      <div className="flex-1 flex flex-col h-full overflow-y-auto overflow-x-hidden relative">
        <main className="p-8 md:p-12 max-w-[1500px] w-full mx-auto pb-24">
          <Outlet context={{ data, isConnected, latestVital, timeWindow, setTimeWindow, loadingHistory }} />
        </main>
      </div>
    </div>
  );
}
