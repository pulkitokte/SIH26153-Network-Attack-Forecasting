import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import type { AnomalyPoint } from '../../types';

export function AnomalyChart({ data }: { data: AnomalyPoint[] }) {
  return (
    <div className="h-[240px] w-full">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="anomFill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#f59e0b" stopOpacity={0.35} />
              <stop offset="100%" stopColor="#f59e0b" stopOpacity={0.02} />
            </linearGradient>
          </defs>
          <CartesianGrid stroke="rgba(148,211,255,0.08)" vertical={false} />
          <XAxis dataKey="time" tick={{ fill: '#8b9bb4', fontSize: 11 }} axisLine={false} tickLine={false} />
          <YAxis domain={[0, 1]} tick={{ fill: '#8b9bb4', fontSize: 11 }} axisLine={false} tickLine={false} width={36} />
          <Tooltip
            content={({ active, payload, label }) =>
              active && payload?.[0] ? (
                <div className="glass-strong rounded-lg px-3 py-2 text-xs">
                  <p className="font-mono text-mute">{String(label)}</p>
                  <p>Score: {String(payload[0].value)}</p>
                </div>
              ) : null
            }
          />
          <Area type="monotone" dataKey="score" stroke="#f59e0b" fill="url(#anomFill)" strokeWidth={2} />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
