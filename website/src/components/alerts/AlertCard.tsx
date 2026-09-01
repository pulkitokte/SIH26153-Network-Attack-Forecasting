import { AlertTriangle } from 'lucide-react';
import type { AlertItem } from '../../types';
import { RiskBadge } from '../common/RiskBadge';
import { cn } from '../../utils/format';

const rail: Record<AlertItem['severity'], string> = {
  CRITICAL: 'bg-critical',
  HIGH: 'bg-high',
  MEDIUM: 'bg-watch',
  LOW: 'bg-safe',
};

export function AlertCard({ alert }: { alert: AlertItem }) {
  return (
    <article
      className={cn(
        'glass relative overflow-hidden rounded-2xl p-4',
        alert.simulated ? 'fade-up ring-1 ring-critical/30' : '',
      )}
    >
      <span className={cn('absolute inset-y-0 left-0 w-1', rail[alert.severity])} />
      <div className="flex flex-wrap items-start justify-between gap-3 pl-2">
        <div className="min-w-0">
          <div className="mb-1 flex flex-wrap items-center gap-2">
            <RiskBadge severity={alert.severity} />
            <span className="font-mono text-[11px] text-mute">{alert.timestamp}</span>
            {alert.simulated ? (
              <span className="rounded-full border border-cyan/30 px-2 py-0.5 font-mono text-[10px] uppercase text-cyan">
                Simulated
              </span>
            ) : null}
          </div>
          <h3 className="flex items-center gap-2 text-sm font-semibold">
            <AlertTriangle className="h-4 w-4 text-high" />
            {alert.title}
          </h3>
          <p className="mt-1 text-xs text-mute">
            {alert.threatType} · Probability {alert.probability}% · {alert.forecastWindow}
          </p>
        </div>
        <span className="rounded-full border border-white/10 px-2.5 py-0.5 font-mono text-[11px] text-mute">
          {alert.status}
        </span>
      </div>
      <p className="mt-3 pl-2 text-xs text-ink/80">
        <span className="text-mute">Recommended action: </span>
        {alert.recommendedAction}
      </p>
    </article>
  );
}
