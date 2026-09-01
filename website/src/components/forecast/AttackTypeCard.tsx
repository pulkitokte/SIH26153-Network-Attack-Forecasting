import type { AttackTypeForecast } from '../../types';
import { RiskBadge } from '../common/RiskBadge';

const barColor: Record<string, string> = {
  CRITICAL: 'bg-critical',
  HIGH: 'bg-high',
  WATCH: 'bg-watch',
  SAFE: 'bg-safe',
};

export function AttackTypeCard({ item, delay = 0 }: { item: AttackTypeForecast; delay?: number }) {
  return (
    <article className="glass fade-up rounded-2xl p-4" style={{ animationDelay: `${delay}ms` }}>
      <div className="mb-3 flex items-start justify-between gap-3">
        <div>
          <h3 className="text-sm font-semibold">{item.type}</h3>
          <p className="mt-1 text-xs text-mute">{item.description}</p>
        </div>
        <RiskBadge level={item.risk} />
      </div>
      <div className="flex items-end justify-between">
        <p className="font-mono text-2xl font-semibold">{item.probability}%</p>
        <p className="text-[11px] uppercase tracking-wide text-mute">Probability</p>
      </div>
      <div className="mt-3 h-1.5 overflow-hidden rounded-full bg-white/8">
        <div
          className={`h-full rounded-full ${barColor[item.risk]}`}
          style={{ width: `${item.probability}%` }}
        />
      </div>
    </article>
  );
}
