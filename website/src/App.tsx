import { Navigate, Route, Routes } from 'react-router-dom';
import { AppLayout } from './components/layout/AppLayout';
import { Dashboard } from './pages/Dashboard';
import { LiveTraffic } from './pages/LiveTraffic';
import { AttackForecast } from './pages/AttackForecast';
import { ThreatIntelligence } from './pages/ThreatIntelligence';
import { Analytics } from './pages/Analytics';
import { Alerts } from './pages/Alerts';
import { ModelPerformance } from './pages/ModelPerformance';
import { SystemArchitecture } from './pages/SystemArchitecture';
import { Settings } from './pages/Settings';

export default function App() {
  return (
    <AppLayout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/traffic" element={<LiveTraffic />} />
        <Route path="/forecast" element={<AttackForecast />} />
        <Route path="/intelligence" element={<ThreatIntelligence />} />
        <Route path="/analytics" element={<Analytics />} />
        <Route path="/alerts" element={<Alerts />} />
        <Route path="/model" element={<ModelPerformance />} />
        <Route path="/architecture" element={<SystemArchitecture />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AppLayout>
  );
}
