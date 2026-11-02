import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import DashboardLayout from './layouts/DashboardLayout';
import Overview from './pages/Overview';
import DataExplorer from './pages/DataExplorer';
import Analysis from './pages/Analysis';
import Prediction from './pages/Prediction';
import ModelComparison from './pages/ModelComparison';
import Insights from './pages/Insights';

export default function App() {
  return (
    <DashboardLayout>
      <Routes>
        <Route path="/" element={<Overview />} />
        <Route path="/explorer" element={<DataExplorer />} />
        <Route path="/analysis" element={<Analysis />} />
        <Route path="/predict" element={<Prediction />} />
        <Route path="/models" element={<ModelComparison />} />
        <Route path="/insights" element={<Insights />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </DashboardLayout>
  );
}
