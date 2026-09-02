import { Line, LineChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import type { TrafficPoint } from '../../types';
import { formatCompact } from '../../utils/format';

function TooltipBody({
  active,
  payload,
  label,
}: {
  active?: boolean;
  payload?: Array<{ value: number; dataKey: string }>;
  label?: string;
}) {
  if (!active || !payload?.length) return null;
  return (
    <div className="glass-strong rounded-lg px-3 py-2 text-xs">
      <p className="mb-1 font-mono text-mute">{label}</p>
      {payload.map((p) => (
        <p key={p.dataKey} className="text-ink">
          {p.dataKey}: {p.dataKey === 'bytes' ? formatCompact(p.value) : p.value}
        </p>
      ))}
    </div>
  );
}

export function TrafficChart({ data }: { data: TrafficPoint[] }) {
  return (
    <div className="h-[260px] w-full">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
          <CartesianGrid stroke="rgba(148,211,255,0.08)" vertical={false} />
          <XAxis dataKey="time" tick={{ fill: '#8b9bb4', fontSize: 10 }} minTickGap={24} axisLine={false} tickLine={false} />
          <YAxis tick={{ fill: '#8b9bb4', fontSize: 11 }} axisLine={false} tickLine={false} width={48} tickFormatter={(v: number) => formatCompact(v)} />
          <Tooltip content={<TooltipBody />} />
          <Line type="monotone" dataKey="packets" stroke="#22d3ee" strokeWidth={2} dot={false} isAnimationActive={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
