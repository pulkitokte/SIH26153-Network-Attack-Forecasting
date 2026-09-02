import { useEffect, useState } from 'react';
import { DataTable } from '../components/common/DataTable';
import { ProtocolChart } from '../components/charts/ProtocolChart';
import { TrafficChart } from '../components/traffic/TrafficChart';
import { SectionHeader } from '../components/common/SectionHeader';
import { RiskBadge } from '../components/common/RiskBadge';
import { useSimulation } from '../context/SimulationContext';
import { formatBytes, formatCompact } from '../utils/format';
import { getAnomalyLabel, getRiskLevel } from '../utils/risk';
import type { TrafficFlow } from '../types';

export function LiveTraffic() {
  const { snapshot, series, flows } = useSimulation();
  const [liveSeries, setLiveSeries] = useState(series);

  useEffect(() => {
    setLiveSeries(series);
  }, [series]);

  useEffect(() => {
    const id = window.setInterval(() => {
      setLiveSeries((prev) => {
        const last = prev[prev.length - 1];
        const nextPackets = Math.max(8_000, (last?.packets ?? snapshot.packetsPerSec) + (Math.random() - 0.42) * 1800);
        const point = {
          time: new Date().toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
          timestamp: Date.now(),
          packets: Math.round(nextPackets),
          bytes: Math.round(nextPackets * 620),
          anomaly: snapshot.anomalyScore,
        };
        return [...prev.slice(-23), point];
      });
    }, 1500);
    return () => window.clearInterval(id);
  }, [snapshot.anomalyScore, snapshot.packetsPerSec]);

  return (
    <div className="space-y-6">
      <SectionHeader
        eyebrow="Live capture"
        title="Live Network Traffic"
        subtitle="Simulated flow telemetry using private RFC1918 addresses. No personal data."
      />
      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        {[
          { label: 'Packets/sec', value: formatCompact(snapshot.packetsPerSec) },
          { label: 'Bytes/sec', value: formatBytes(snapshot.bytesPerSec) },
          { label: 'Active connections', value: formatCompact(snapshot.activeConnections) },
          { label: 'Anomaly score', value: snapshot.anomalyScore.toFixed(2) },
          { label: 'Current network risk', value: `${snapshot.networkRisk}%` },
          { label: 'Anomaly label', value: getAnomalyLabel(snapshot.anomalyScore) },
        ].map((card) => (
          <article key={card.label} className="glass rounded-2xl p-4">
            <p className="text-xs uppercase tracking-[0.14em] text-mute">{card.label}</p>
            <p className="mt-2 font-mono text-2xl font-semibold">{card.value}</p>
          </article>
        ))}
      </section>
      <section className="grid gap-4 xl:grid-cols-5">
        <div className="glass rounded-2xl p-5 xl:col-span-3">
          <h2 className="mb-3 text-sm font-semibold">Packets / sec</h2>
          <TrafficChart data={liveSeries} />
        </div>
        <div className="glass rounded-2xl p-5 xl:col-span-2">
          <div className="mb-2 flex items-center justify-between">
            <h2 className="text-sm font-semibold">Protocol distribution</h2>
            <RiskBadge level={getRiskLevel(snapshot.networkRisk)} />
          </div>
          <ProtocolChart data={snapshot.protocolDistribution} />
        </div>
      </section>
      <section className="glass rounded-2xl p-5">
        <h2 className="mb-3 text-sm font-semibold">Recent flows</h2>
        <DataTable<TrafficFlow>
          dense
          rowKey={(row) => row.id}
          rows={flows}
          columns={[
            { key: 'time', header: 'Time', render: (r) => <span className="font-mono text-xs">{r.time}</span> },
            { key: 'src', header: 'Source IP', render: (r) => <span className="font-mono text-xs">{r.sourceIp}</span> },
            { key: 'dst', header: 'Destination IP', render: (r) => <span className="font-mono text-xs">{r.destinationIp}</span> },
            { key: 'proto', header: 'Protocol', render: (r) => r.protocol },
            { key: 'pkts', header: 'Packets', render: (r) => r.packets.toLocaleString() },
            { key: 'bytes', header: 'Bytes', render: (r) => formatBytes(r.bytes) },
            { key: 'score', header: 'Anomaly Score', render: (r) => r.anomalyScore.toFixed(2) },
            {
              key: 'status',
              header: 'Status',
              render: (r) => (
                <span className={r.status === 'Normal' ? 'text-safe' : r.status === 'Critical' ? 'text-critical' : 'text-high'}>
                  {r.status}
                </span>
              ),
            },
          ]}
        />
      </section>
    </div>
  );
}
