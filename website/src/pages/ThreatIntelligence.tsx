import { useEffect, useState } from 'react';
import { AnomalyChart } from '../components/charts/AnomalyChart';
import { PipelineDiagram } from '../components/pipeline/PipelineDiagram';
import { SectionHeader } from '../components/common/SectionHeader';
import { DataTable } from '../components/common/DataTable';
import { useSimulation } from '../context/SimulationContext';
import { getDatasets, getPipeline } from '../services/api';
import { MOCK_NOTE } from '../data/mock';
import type { DatasetInfo, PipelineStage } from '../types';
import { ArrowDown } from 'lucide-react';

const FLOW = ['Traffic Data', 'Feature Extraction', 'Isolation Forest', 'Anomaly Score', 'LSTM/GRU Forecasting', 'Attack Probability'];

export function ThreatIntelligence() {
  const { data } = useSimulation();
  const [sets, setSets] = useState<DatasetInfo[]>([]);
  const [stages, setStages] = useState<PipelineStage[]>([]);

  useEffect(() => {
    void getDatasets().then(setSets);
    void getPipeline().then(setStages);
  }, []);

  return (
    <div className="space-y-6">
      <SectionHeader
        eyebrow="Detection engine"
        title="Threat Intelligence"
        subtitle="Isolation Forest flags abnormal traffic. The forecasting model then estimates whether those anomalies will become an attack."
      />
      <section className="glass rounded-2xl p-5">
        <h2 className="text-lg font-semibold">Anomaly Detection Engine</h2>
        <div className="mt-4 flex flex-wrap items-center gap-2">
          {FLOW.map((step, i) => (
            <div key={step} className="flex items-center gap-2">
              <span className="rounded-full border border-cyan/25 bg-cyan/10 px-3 py-1.5 text-xs font-medium text-cyan-2">
                {step}
              </span>
              {i < FLOW.length - 1 ? <ArrowDown className="h-3.5 w-3.5 rotate-[-90deg] text-mute" /> : null}
            </div>
          ))}
        </div>
      </section>
      <section className="grid gap-4 xl:grid-cols-2">
        <div className="glass rounded-2xl p-5">
          <h2 className="mb-3 text-sm font-semibold">Anomaly score over time</h2>
          <AnomalyChart data={data.anomalySeries} />
          <p className="mt-3 text-xs text-mute">Example path: Normal 0.12 → Suspicious 0.54 → Anomalous 0.81 → Critical 0.93</p>
        </div>
        <div className="glass rounded-2xl p-5">
          <h2 className="mb-3 text-sm font-semibold">Current window</h2>
          <ul className="space-y-3">
            {data.anomalySeries.map((p) => (
              <li key={p.time + p.score} className="flex items-center justify-between rounded-xl border border-white/8 px-3 py-2">
                <span className="font-mono text-xs text-mute">{p.time}</span>
                <span className="text-sm">{p.label}</span>
                <span className="font-mono text-sm">{p.score.toFixed(2)}</span>
              </li>
            ))}
          </ul>
        </div>
      </section>
      <section>
        <h2 className="mb-3 text-lg font-semibold">AI model pipeline</h2>
        <PipelineDiagram stages={stages} />
      </section>
      <section className="glass rounded-2xl p-5">
        <h2 className="text-lg font-semibold">Datasets</h2>
        <p className="mt-1 mb-4 text-xs text-mute">{MOCK_NOTE}</p>
        <DataTable<DatasetInfo>
          rowKey={(r) => r.name}
          rows={sets}
          columns={[
            { key: 'name', header: 'Dataset', render: (r) => <span className="font-medium">{r.name}</span> },
            { key: 'type', header: 'Traffic type', render: (r) => r.trafficType },
            { key: 'cat', header: 'Attack categories', render: (r) => r.attackCategories },
            { key: 'rec', header: 'Records', render: (r) => r.records },
            { key: 'status', header: 'Status', render: (r) => r.status },
          ]}
        />
      </section>
    </div>
  );
}
