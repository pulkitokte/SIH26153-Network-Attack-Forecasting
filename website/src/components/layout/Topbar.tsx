import { Bell, Menu, User } from 'lucide-react';
import { LiveIndicator } from '../common/LiveIndicator';
import { SimulationControls } from '../simulation/SimulationControls';
import { useSimulation } from '../../context/SimulationContext';
import { getRiskLevel } from '../../utils/risk';
import { RiskBadge } from '../common/RiskBadge';

interface Props {
  onMenu: () => void;
}

export function Topbar({ onMenu }: Props) {
  const { data, lastUpdated, alerts } = useSimulation();
  const activeAlerts = alerts.filter((a) => a.status === 'ACTIVE').length;

  return (
    <header className="glass-strong flex h-16 items-center justify-between gap-4 border-b border-white/8 px-4 lg:px-6">
      <div className="flex min-w-0 items-center gap-3">
        <button
          type="button"
          className="rounded-lg border border-white/10 p-2 text-mute hover:text-ink lg:hidden"
          onClick={onMenu}
          aria-label="Open navigation"
        >
          <Menu className="h-4 w-4" />
        </button>
        <div className="min-w-0">
          <div className="flex flex-wrap items-center gap-2">
            <LiveIndicator label="AI Engine Online" online={data.engineOnline} className="text-safe" />
            <span className="hidden h-3 w-px bg-white/10 sm:block" />
            <LiveIndicator />
          </div>
          <p className="mt-0.5 hidden font-mono text-[11px] text-mute md:block">Last updated {lastUpdated}</p>
        </div>
      </div>
      <div className="flex items-center gap-2 sm:gap-3">
        <RiskBadge level={getRiskLevel(data.currentRisk)} />
        <SimulationControls compact />
        <button type="button" className="relative rounded-lg border border-white/10 p-2 text-mute hover:text-ink" aria-label="Notifications">
          <Bell className="h-4 w-4" />
          {activeAlerts > 0 ? (
            <span className="absolute -right-1 -top-1 flex h-4 min-w-4 items-center justify-center rounded-full bg-critical px-1 font-mono text-[10px] text-white">
              {activeAlerts}
            </span>
          ) : null}
        </button>
        <div className="hidden items-center gap-2 rounded-xl border border-white/10 px-2.5 py-1.5 md:flex">
          <span className="flex h-7 w-7 items-center justify-center rounded-full bg-cyan/15 text-cyan">
            <User className="h-3.5 w-3.5" />
          </span>
          <div className="leading-tight">
            <p className="text-xs font-medium">SOC Analyst</p>
            <p className="font-mono text-[10px] text-mute">Demo session</p>
          </div>
        </div>
      </div>
    </header>
  );
}
