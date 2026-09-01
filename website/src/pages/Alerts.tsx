import { AlertCard } from '../components/alerts/AlertCard';
import { SectionHeader } from '../components/common/SectionHeader';
import { useSimulation } from '../context/SimulationContext';

export function Alerts() {
  const { alerts } = useSimulation();
  const active = alerts.filter((a) => a.status === 'ACTIVE').length;

  return (
    <div className="space-y-6">
      <SectionHeader
        eyebrow="Predictive alerts"
        title="Alerts"
        subtitle={`${active} active predictive alerts. These fire on forecasted risk, not only on confirmed intrusion.`}
      />
      <div className="grid gap-3">
        {alerts.map((alert) => (
          <AlertCard key={alert.id} alert={alert} />
        ))}
      </div>
    </div>
  );
}
