import type { RiskLevel, AlertSeverity } from '../../types';
import { cn } from '../../utils/format';

const riskStyles: Record<RiskLevel, string> = {
  SAFE: 'text-safe border-safe/30 bg-safe/10',
  WATCH: 'text-watch border-watch/30 bg-watch/10',
  HIGH: 'text-high border-high/30 bg-high/10',
  CRITICAL: 'text-critical border-critical/30 bg-critical/10',
};

const severityStyles: Record<AlertSeverity, string> = {
  LOW: 'text-safe border-safe/30 bg-safe/10',
  MEDIUM: 'text-watch border-watch/30 bg-watch/10',
  HIGH: 'text-high border-high/30 bg-high/10',
  CRITICAL: 'text-critical border-critical/30 bg-critical/10',
};

interface Props {
  level?: RiskLevel;
  severity?: AlertSeverity;
  className?: string;
}

export function RiskBadge({ level, severity, className }: Props) {
  const label = level ?? severity ?? 'SAFE';
  const style = level ? riskStyles[level] : severity ? severityStyles[severity] : riskStyles.SAFE;
  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full border px-2.5 py-0.5 font-mono text-[11px] font-medium tracking-wide uppercase',
        style,
        className,
      )}
    >
      {label}
    </span>
  );
}
