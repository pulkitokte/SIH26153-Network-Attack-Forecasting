import { useEffect, useState } from 'react';
import { Line, LineChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { ModelMetricCard } from '../components/model/ModelMetricCard';
import { SectionHeader } from '../components/common/SectionHeader';
import { DataTable } from '../components/common/DataTable';
import { getModelMetrics } from '../services/api';
import { MOCK_NOTE } from '../data/mock';
import type { ConfusionMatrix, ModelComparisonRow, ModelMetrics, RocPoint } from '../types';

export function ModelPerformance() {
  const [metrics, setMetrics] = useState<ModelMetrics | null>(null);
  const [comparison, setComparison] = useState<ModelComparisonRow[]>([]);
  const [confusion, setConfusion] = useState<ConfusionMatrix | null>(null);
  const [roc, setRoc] = useState<RocPoint[]>([]);
  const [pr, setPr] = useState<RocPoint[]>([]);

  useEffect(() => {
    void getModelMetrics().then((res) => {
      setMetrics(res.metrics);
      setComparison(res.comparison);
      setConfusion(res.confusion);
      setRoc(res.roc);
      setPr(res.pr);
    });
  }, []);

  if (!metrics || !confusion) return <p className="text-sm text-mute">Loading model metrics…</p>;

  return (
    <div className="space-y-6">
      <SectionHeader
        eyebrow="Evaluation"
        title="Model Performance"
        subtitle={MOCK_NOTE}
      />
      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
        <ModelMetricCard label="Accuracy" value={`${metrics.accuracy}%`} hint="Demo / mock value" />
        <ModelMetricCard label="Precision" value={`${metrics.precision}%`} hint="Demo / mock value" />
        <ModelMetricCard label="Recall" value={`${metrics.recall}%`} hint="Demo / mock value" />
        <ModelMetricCard label="F1 Score" value={`${metrics.f1}%`} hint="Demo / mock value" />
        <ModelMetricCard label="ROC-AUC" value={`${metrics.rocAuc}%`} hint="Demo / mock value" />
      </section>
      <section className="grid gap-4 xl:grid-cols-2">
        <article className="glass rounded-2xl p-5">
          <h2 className="mb-3 text-sm font-semibold">Confusion matrix</h2>
          <p className="mb-4 text-xs text-mute">Predicted → columns · Actual ↓ rows. Mock counts only.</p>
          <table className="w-full text-center text-xs">
            <thead>
              <tr>
                <th className="p-2" />
                {confusion.labels.map((label) => (
                  <th key={label} className="p-2 font-medium text-mute">
                    Pred {label}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {confusion.labels.map((label, i) => (
                <tr key={label}>
                  <th className="p-2 text-left font-medium text-mute">Actual {label}</th>
                  {confusion.values[i]?.map((value, j) => (
                    <td key={`${label}-${j}`} className="p-2">
                      <div
                        className={`rounded-xl border border-white/10 py-6 font-mono text-lg ${i === j ? 'bg-safe/15 text-safe' : 'bg-critical/10 text-critical'}`}
                      >
                        {value}
                      </div>
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </article>
        <article className="glass rounded-2xl p-5">
          <h2 className="mb-3 text-sm font-semibold">ROC curve</h2>
          <ResponsiveContainer width="100%" height={260}>
            <LineChart data={roc}>
              <CartesianGrid stroke="rgba(148,211,255,0.08)" />
              <XAxis dataKey="fpr" tick={{ fill: '#8b9bb4', fontSize: 11 }} />
              <YAxis dataKey="tpr" tick={{ fill: '#8b9bb4', fontSize: 11 }} />
              <Tooltip contentStyle={{ background: '#0b1220', border: '1px solid rgba(148,211,255,0.15)' }} />
              <Line type="monotone" dataKey="tpr" stroke="#22d3ee" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </article>
        <article className="glass rounded-2xl p-5">
          <h2 className="mb-3 text-sm font-semibold">Precision / recall</h2>
          <ResponsiveContainer width="100%" height={260}>
            <LineChart data={pr}>
              <CartesianGrid stroke="rgba(148,211,255,0.08)" />
              <XAxis dataKey="fpr" tick={{ fill: '#8b9bb4', fontSize: 11 }} name="Recall" />
              <YAxis tick={{ fill: '#8b9bb4', fontSize: 11 }} />
              <Tooltip contentStyle={{ background: '#0b1220', border: '1px solid rgba(148,211,255,0.15)' }} />
              <Line type="monotone" dataKey="tpr" stroke="#f59e0b" strokeWidth={2} dot={false} name="Precision" />
            </LineChart>
          </ResponsiveContainer>
          <p className="mt-2 text-[11px] text-mute">X = recall (mapped), Y = precision. Mock curve.</p>
        </article>
        <article className="glass rounded-2xl p-5">
          <h2 className="mb-3 text-sm font-semibold">Model comparison</h2>
          <DataTable<ModelComparisonRow>
            rowKey={(r) => r.model}
            rows={comparison}
            columns={[
              { key: 'model', header: 'Model', render: (r) => r.model },
              { key: 'acc', header: 'Accuracy', render: (r) => `${r.accuracy}%` },
              { key: 'f1', header: 'F1', render: (r) => `${r.f1}%` },
              { key: 'role', header: 'Role', render: (r) => r.role },
            ]}
          />
        </article>
      </section>
    </div>
  );
}
