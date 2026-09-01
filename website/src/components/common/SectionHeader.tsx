import type { ReactNode } from 'react';
import { cn } from '../../utils/format';

interface Props {
  eyebrow?: string;
  title: string;
  subtitle?: string;
  action?: ReactNode;
  className?: string;
}

export function SectionHeader({ eyebrow, title, subtitle, action, className }: Props) {
  return (
    <div className={cn('mb-4 flex flex-wrap items-end justify-between gap-3', className)}>
      <div>
        {eyebrow ? (
          <p className="mb-1 font-mono text-[11px] uppercase tracking-[0.18em] text-cyan/80">{eyebrow}</p>
        ) : null}
        <h2 className="text-lg font-semibold tracking-tight text-ink">{title}</h2>
        {subtitle ? <p className="mt-1 max-w-2xl text-sm text-mute">{subtitle}</p> : null}
      </div>
      {action}
    </div>
  );
}
