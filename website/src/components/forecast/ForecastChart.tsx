import { Area, AreaChart, CartesianGrid, ReferenceArea, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import type { ForecastPoint } from '../../types';

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
  const historical = payload.find((p) => p.dataKey === 'historical')?.value;
  const forecast = payload.find((p) => p.dataKey === 'forecast')?.value;
  return (
    <div className="glass-strong rounded-lg px-3 py-2 text-xs">
      <p className="mb-1 font-mono text-mute">{label}</p>
      {historical != null ? <p className="text-ink">Historical: {historical}%</p> : null}
      {forecast != null ? <p className="text-cyan">Forecast: {forecast}%</p> : null}
    </div>
  );
}

export function ForecastChart({ data }: { data: ForecastPoint[] }) {
  const now = data.find((d) => d.isNow)?.time;
  const forecastStart = now ?? data[Math.floor(data.length / 2)]?.time;

  return (
    <div className="h-[280px] w-full">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data} margin={{ top: 8, right: 12, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="histFill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#22d3ee" stopOpacity={0.28} />
              <stop offset="100%" stopColor="#22d3ee" stopOpacity={0.02} />
            </linearGradient>
            <linearGradient id="fcFill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#fb7185" stopOpacity={0.32} />
              <stop offset="100%" stopColor="#fb7185" stopOpacity={0.02} />
            </linearGradient>
          </defs>
          <CartesianGrid stroke="rgba(148,211,255,0.08)" vertical={false} />
          <XAxis dataKey="time" tick={{ fill: '#8b9bb4', fontSize: 11 }} axisLine={false} tickLine={false} />
          <YAxis
            domain={[0, 100]}
            ticks={[0, 25, 50, 75, 100]}
            allowDataOverflow
            tick={{ fill: '#8b9bb4', fontSize: 11 }}
            axisLine={false}
            tickLine={false}
            width={42}
            tickFormatter={(value: number) => `${value}%`}
          />
          <Tooltip content={<TooltipBody />} />
          {forecastStart ? (
            <ReferenceArea x1={forecastStart} x2={data[data.length - 1]?.time} fill="rgba(251,113,133,0.06)" />
          ) : null}
          {now ? <ReferenceLine x={now} stroke="#67e8f9" strokeDasharray="3 3" label={{ value: 'Now', fill: '#67e8f9', fontSize: 11 }} /> : null}
          <Area
            type="monotone"
            dataKey="historical"
            stroke="#22d3ee"
            fill="url(#histFill)"
            strokeWidth={2}
            dot={false}
            connectNulls={false}
            name="Historical"
          />
          <Area
            type="monotone"
            dataKey="forecast"
            stroke="#fb7185"
            fill="url(#fcFill)"
            strokeWidth={2}
            strokeDasharray="6 4"
            dot={false}
            connectNulls
            name="Forecast"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
