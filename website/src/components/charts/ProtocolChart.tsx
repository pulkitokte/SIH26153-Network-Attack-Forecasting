import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts';
import type { ProtocolShare } from '../../types';

const COLORS = ['#22d3ee', '#67e8f9', '#38bdf8', '#818cf8', '#f59e0b', '#fb7185'];

export function ProtocolChart({ data }: { data: ProtocolShare[] }) {
  return (
    <div className="grid h-[240px] grid-cols-[minmax(0,1fr)_7.5rem] items-center gap-3">
      <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie data={data} dataKey="value" nameKey="protocol" innerRadius={54} outerRadius={78} paddingAngle={3} stroke="none">
              {data.map((entry, i) => (
                <Cell key={entry.protocol} fill={COLORS[i % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip
              content={({ active, payload }) =>
                active && payload?.[0] ? (
                  <div className="glass-strong rounded-lg px-3 py-2 text-xs">
                    {String(payload[0].name)}: {String(payload[0].value)}%
                  </div>
                ) : null
              }
            />
          </PieChart>
        </ResponsiveContainer>
      <ul className="w-28 shrink-0 space-y-1.5 text-xs">
        {data.map((d, i) => (
          <li key={d.protocol} className="flex items-center justify-between gap-2 text-mute">
            <span className="flex items-center gap-2">
              <span className="h-2 w-2 rounded-full" style={{ background: COLORS[i % COLORS.length] }} />
              {d.protocol}
            </span>
            <span className="font-mono text-ink">{d.value}%</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
