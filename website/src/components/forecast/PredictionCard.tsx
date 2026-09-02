import { ShieldAlert } from 'lucide-react';
import type { AttackType, RiskLevel } from '../../types';
import { getRiskLevel } from '../../utils/risk';
import { RiskBadge } from '../common/RiskBadge';

interface Props {
  probability: number;
  predictedAttack: AttackType;
  confidence: number;
  horizon: number;
  risk?: RiskLevel;
}

export function PredictionCard({ probability, predictedAttack, confidence, horizon, risk }: Props) {
  const level = risk ?? getRiskLevel(probability);
  return (
    <article className="glass relative overflow-hidden rounded-2xl p-6">
      <div className="pointer-events-none absolute -right-10 -top-10 h-40 w-40 rounded-full bg-critical/10" />
      <p className="font-mono text-[11px] uppercase tracking-[0.2em] text-mute">Next {horizon} minutes</p>
      <div className="mt-4 flex items-end gap-3">
        <p className="font-mono text-6xl font-semibold tracking-tight text-ink">{Math.round(probability)}%</p>
        <p className="mb-2 text-sm text-mute">Probability of attack</p>
      </div>
      <div className="mt-5 grid gap-3 sm:grid-cols-3">
        <div className="rounded-xl border border-white/8 bg-white/[0.03] p-3">
          <p className="text-[11px] uppercase tracking-wide text-mute">Predicted attack</p>
          <p className="mt-1 flex items-center gap-2 text-sm font-semibold">
            <ShieldAlert className="h-4 w-4 text-critical" />
            {predictedAttack}
          </p>
        </div>
        <div className="rounded-xl border border-white/8 bg-white/[0.03] p-3">
          <p className="text-[11px] uppercase tracking-wide text-mute">Confidence</p>
          <p className="mt-1 font-mono text-sm font-semibold">{confidence}%</p>
        </div>
        <div className="rounded-xl border border-white/8 bg-white/[0.03] p-3">
          <p className="text-[11px] uppercase tracking-wide text-mute">Risk</p>
          <div className="mt-1">
            <RiskBadge level={level} />
          </div>
        </div>
      </div>
    </article>
  );
}
