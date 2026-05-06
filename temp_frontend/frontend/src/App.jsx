import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Dashboard from './components/dashboard/Dashboard';
import Overview from './components/dashboard/Overview';
import HeartRateView from './components/dashboard/HeartRateView';
import SpO2View from './components/dashboard/SpO2View';
import BloodPressureView from './components/dashboard/BloodPressureView';
import AlertsView from './components/dashboard/AlertsView';
import SettingsView from './components/dashboard/SettingsView';
import HistoryView from './components/dashboard/HistoryView';

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-[#f5f2eb] text-[#2c2825] font-sans">
        <Routes>
          <Route path="/" element={<Dashboard />}>
            <Route index element={<Overview />} />
            <Route path="heart-rate" element={<HeartRateView />} />
            <Route path="spo2" element={<SpO2View />} />
            <Route path="blood-pressure" element={<BloodPressureView />} />
            <Route path="alerts" element={<AlertsView />} />
            <Route path="history" element={<HistoryView />} />
            <Route path="settings" element={<SettingsView />} />
          </Route>
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
