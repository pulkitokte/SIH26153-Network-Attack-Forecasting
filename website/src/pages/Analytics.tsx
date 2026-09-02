import { useEffect, useState, type ReactNode } from 'react';
import { Bar, BarChart, CartesianGrid, Cell, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { ProtocolChart } from '../components/charts/ProtocolChart';
import { SectionHeader } from '../components/common/SectionHeader';
import { getAnalytics } from '../services/api';
import type { AnalyticsBundle, TimeRange } from '../types';
import { cn } from '../utils/format';
import { getRiskLevel } from '../utils/risk';

const RANGES: { id: TimeRange; label: string }[] = [
  { id: '15m', label: 'Last 15 min' },
  { id: '1h', label: 'Last 1 hour' },
  { id: '6h', label: 'Last 6 hours' },
  { id: '24h', label: 'Last 24 hours' },
];

const heatColor = (risk: number) => {
  const level = getRiskLevel(risk);
  if (level === 'SAFE') return 'bg-safe/25';
  if (level === 'WATCH') return 'bg-watch/30';
  if (level === 'HIGH') return 'bg-high/40';
  return 'bg-critical/50';
};

export function Analytics() {
  const [range, setRange] = useState<TimeRange>('1h');
  const [bundle, setBundle] = useState<AnalyticsBundle | null>(null);

  useEffect(() => {
    void getAnalytics(range).then(setBundle);
  }, [range]);

  if (!bundle) {
    return <p className="text-sm text-mute">Loading analytics…</p>;
  }

  return (
    <div className="space-y-6">
      <SectionHeader
        eyebrow="Historical view"
        title="Analytics"
        subtitle="Mock analytics for the demo. Swap getAnalytics() with GET /dashboard range queries later."
        action={
          <div className="flex flex-wrap gap-1 rounded-xl border border-white/10 p-1">
            {RANGES.map((r) => (
              <button
                key={r.id}
                type="button"
                onClick={() => setRange(r.id)}
                className={cn(
                  'rounded-lg px-3 py-1.5 text-xs',
                  range === r.id ? 'bg-cyan/15 text-cyan' : 'text-mute hover:text-ink',
                )}
              >
                {r.label}
              </button>
            ))}
          </div>
        }
      />
      <section className="grid gap-4 xl:grid-cols-2">
        <ChartCard title="Attack distribution">
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={bundle.attackDistribution}>
              <CartesianGrid stroke="rgba(148,211,255,0.08)" vertical={false} />
              <XAxis dataKey="name" tick={{ fill: '#8b9bb4', fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: '#8b9bb4', fontSize: 11 }} axisLine={false} tickLine={false} />
              <Tooltip contentStyle={{ background: '#0b1220', border: '1px solid rgba(148,211,255,0.15)' }} />
              <Bar dataKey="value" radius={[6, 6, 0, 0]}>
                {bundle.attackDistribution.map((d) => (
                  <Cell key={d.name} fill={d.name === 'DDoS' ? '#fb7185' : '#22d3ee'} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
        <ChartCard title="Traffic volume">
          <ResponsiveContainer width="100%" height={240}>
            <LineChart data={bundle.trafficVolume}>
              <CartesianGrid stroke="rgba(148,211,255,0.08)" vertical={false} />
              <XAxis dataKey="time" tick={{ fill: '#8b9bb4', fontSize: 10 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: '#8b9bb4', fontSize: 11 }} axisLine={false} tickLine={false} />
              <Tooltip contentStyle={{ background: '#0b1220', border: '1px solid rgba(148,211,255,0.15)' }} />
              <Line type="monotone" dataKey="volume" stroke="#67e8f9" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </ChartCard>
        <ChartCard title="Anomaly score trend">
          <ResponsiveContainer width="100%" height={240}>
            <LineChart data={bundle.anomalyTrend}>
              <CartesianGrid stroke="rgba(148,211,255,0.08)" vertical={false} />
              <XAxis dataKey="time" tick={{ fill: '#8b9bb4', fontSize: 10 }} axisLine={false} tickLine={false} />
              <YAxis domain={[0, 1]} tick={{ fill: '#8b9bb4', fontSize: 11 }} axisLine={false} tickLine={false} />
              <Tooltip contentStyle={{ background: '#0b1220', border: '1px solid rgba(148,211,255,0.15)' }} />
              <Line type="monotone" dataKey="score" stroke="#f59e0b" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </ChartCard>
        <ChartCard title="Attack probability trend">
          <ResponsiveContainer width="100%" height={240}>
            <LineChart data={bundle.probabilityTrend}>
              <CartesianGrid stroke="rgba(148,211,255,0.08)" vertical={false} />
              <XAxis dataKey="time" tick={{ fill: '#8b9bb4', fontSize: 10 }} axisLine={false} tickLine={false} />
              <YAxis domain={[0, 100]} tick={{ fill: '#8b9bb4', fontSize: 11 }} axisLine={false} tickLine={false} />
              <Tooltip contentStyle={{ background: '#0b1220', border: '1px solid rgba(148,211,255,0.15)' }} />
              <Line type="monotone" dataKey="probability" stroke="#fb7185" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </ChartCard>
      </section>
      <section className="grid gap-4 xl:grid-cols-5">
        <div className="glass rounded-2xl p-5 xl:col-span-2">
          <h2 className="mb-2 text-sm font-semibold">Protocol distribution</h2>
          <ProtocolChart data={bundle.protocolDistribution} />
        </div>
        <div className="glass rounded-2xl p-5 xl:col-span-3">
          <h2 className="mb-3 text-sm font-semibold">Hourly risk heatmap</h2>
          <div className="grid grid-cols-6 gap-2 sm:grid-cols-8 lg:grid-cols-12">
            {bundle.hourlyHeatmap.map((cell) => (
              <div key={cell.hour} className={cn('rounded-lg p-2 text-center', heatColor(cell.risk))} title={`${cell.hour} · ${cell.risk}%`}>
                <p className="font-mono text-[10px] text-ink/80">{cell.hour.replace(':00', '')}</p>
                <p className="mt-1 font-mono text-xs">{cell.risk}</p>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}

function ChartCard({ title, children }: { title: string; children: ReactNode }) {
  return (
    <article className="glass rounded-2xl p-5">
      <h2 className="mb-3 text-sm font-semibold">{title}</h2>
      {children}
    </article>
  );
}
