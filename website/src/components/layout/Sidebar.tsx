import { NavLink } from 'react-router-dom';
import {
  Activity,
  Bell,
  Brain,
  Gauge,
  LayoutDashboard,
  Network,
  Radar,
  Settings,
  Shield,
  Workflow,
} from 'lucide-react';
import { cn } from '../../utils/format';

const LINKS = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/traffic', label: 'Live Network Traffic', icon: Activity },
  { to: '/forecast', label: 'Attack Forecast', icon: Radar },
  { to: '/intelligence', label: 'Threat Intelligence', icon: Shield },
  { to: '/analytics', label: 'Analytics', icon: Gauge },
  { to: '/alerts', label: 'Alerts', icon: Bell },
  { to: '/model', label: 'Model Performance', icon: Brain },
  { to: '/architecture', label: 'System Architecture', icon: Workflow },
  { to: '/settings', label: 'Settings', icon: Settings },
];

export function Sidebar({ onNavigate }: { onNavigate?: () => void }) {
  return (
    <aside className="glass-strong flex h-full w-[260px] flex-col border-r border-white/8">
      <div className="border-b border-white/8 px-5 py-5">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl border border-cyan/30 bg-cyan/10">
            <Network className="h-4 w-4 text-cyan" />
          </div>
          <div>
            <p className="text-sm font-semibold tracking-tight">Forecast SOC</p>
            <p className="font-mono text-[10px] uppercase tracking-[0.16em] text-mute">SIH 26153</p>
          </div>
        </div>
      </div>
      <nav className="flex-1 space-y-1 overflow-y-auto p-3 scrollbar-thin">
        {LINKS.map((link) => (
          <NavLink
            key={link.to}
            to={link.to}
            end={link.to === '/'}
            onClick={onNavigate}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm transition',
                isActive
                  ? 'bg-cyan/12 text-cyan shadow-[inset_2px_0_0_0_#22d3ee]'
                  : 'text-mute hover:bg-white/5 hover:text-ink',
              )
            }
          >
            <link.icon className="h-4 w-4 shrink-0" />
            {link.label}
          </NavLink>
        ))}
      </nav>
      <div className="border-t border-white/8 p-4">
        <p className="text-[11px] leading-relaxed text-mute">
          AI Network Attack Forecasting from Network Traffic Data.
        </p>
      </div>
    </aside>
  );
}
