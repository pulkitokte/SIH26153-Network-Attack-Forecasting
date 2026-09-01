import { Activity, Minus, TrendingDown, TrendingUp } from 'lucide-react';
import type { KpiMetric } from '../../types';
import { cn } from '../../utils/format';

const toneRing: Record<KpiMetric['tone'], string> = {
  cyan: 'text-cyan',
  amber: 'text-high',
  red: 'text-critical',
  green: 'text-safe',
  neutral: 'text-mute',
};

export function KpiCard({ metric, delay = 0 }: { metric: KpiMetric; delay?: number }) {
  const TrendIcon = metric.trend.direction === 'up' ? TrendingUp : metric.trend.direction === 'down' ? TrendingDown : Minus;
  const trendColor =
    metric.tone === 'green' || metric.trend.direction === 'down'
      ? 'text-safe'
      : metric.trend.direction === 'up' && (metric.tone === 'red' || metric.tone === 'amber')
        ? 'text-critical'
        : 'text-cyan';

  return (
    <article
      className="glass fade-up rounded-2xl p-4"
      style={{ animationDelay: `${delay}ms` }}
    >
      <div className="mb-3 flex items-center justify-between">
        <p className="text-xs font-medium uppercase tracking-[0.14em] text-mute">{metric.label}</p>
        <Activity className={cn('h-4 w-4', toneRing[metric.tone])} />
      </div>
      <p className="font-mono text-3xl font-semibold tracking-tight text-ink">{metric.value}</p>
      <div className="mt-2 flex items-center justify-between gap-2">
        <p className="text-xs text-mute">{metric.unit}</p>
        <span className={cn('inline-flex items-center gap-1 font-mono text-[11px]', trendColor)}>
          <TrendIcon className="h-3 w-3" />
          {metric.trend.value}
        </span>
      </div>
    </article>
  );
}
