import { ArrowDown, ArrowUp } from 'lucide-react';
import { KpiCard } from '../components/kpi/KpiCard';
import { ForecastChart } from '../components/forecast/ForecastChart';
import { AttackTypeCard } from '../components/forecast/AttackTypeCard';
import { SimulationControls } from '../components/simulation/SimulationControls';
import { LiveIndicator } from '../components/common/LiveIndicator';
import { RiskBadge } from '../components/common/RiskBadge';
import { AnomalyChart } from '../components/charts/AnomalyChart';
import { PipelineDiagram } from '../components/pipeline/PipelineDiagram';
import { useSimulation } from '../context/SimulationContext';
import { getRiskLevel, getRiskCopy } from '../utils/risk';
import { pipelineStages } from '../data/mock';

export function Dashboard() {
  const { data } = useSimulation();
  const risk = getRiskLevel(data.currentRisk);
  const forecastRisk = getRiskLevel(data.attackProbability);

  return (
    <div className="space-y-6">
      <header className="fade-up flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="font-mono text-[11px] uppercase tracking-[0.22em] text-cyan/80">SIH26153 · Predictive SOC</p>
          <h1 className="mt-1 text-3xl font-semibold tracking-tight md:text-4xl">AI Network Attack Forecasting</h1>
          <p className="mt-2 text-mute">Predict threats before they happen.</p>
        </div>
        <LiveIndicator label="AI Engine Online" online={data.engineOnline} className="rounded-full border border-safe/30 bg-safe/10 px-3 py-1.5 text-safe" />
      </header>

      <section className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
        {[
          { q: 'Network status', a: risk, note: getRiskCopy(risk) },
          { q: 'Attack happening now?', a: data.currentRisk >= 81 ? 'Likely active' : 'Not confirmed', note: 'Detection ≠ forecast' },
          { q: 'Attack predicted?', a: forecastRisk === 'SAFE' ? 'No' : `Yes · ${data.predictedAttack}`, note: `Next ${data.forecastHorizonMin} min` },
          { q: 'Model confidence', a: `${data.confidence}%`, note: 'Forecasting engine' },
        ].map((item) => (
          <div key={item.q} className="glass rounded-2xl p-4">
            <p className="text-[11px] uppercase tracking-[0.14em] text-mute">{item.q}</p>
            <p className="mt-2 text-lg font-semibold">{item.a}</p>
            <p className="mt-1 text-xs text-mute">{item.note}</p>
          </div>
        ))}
      </section>

      <SimulationControls />

      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-6">
        {data.kpis.map((metric, i) => (
          <KpiCard key={metric.id} metric={metric} delay={i * 40} />
        ))}
      </section>

      <section className="glass rounded-2xl p-5">
        <div className="mb-4 flex flex-wrap items-start justify-between gap-3">
          <div>
            <h2 className="text-lg font-semibold">Attack Probability Forecast</h2>
            <p className="mt-1 text-sm text-mute">AI prediction based on recent network traffic patterns</p>
          </div>
          <div className="text-right">
            <p className="font-mono text-[11px] uppercase tracking-[0.14em] text-cyan">Forecast: Next {data.forecastHorizonMin} Minutes</p>
            <p className="mt-1 text-xs text-mute">Confidence: {data.confidence}%</p>
          </div>
        </div>
        <ForecastChart data={data.forecastSeries} />
        <div className="mt-4 flex flex-wrap items-center justify-between gap-3 rounded-xl border border-high/25 bg-high/8 px-4 py-3 text-sm">
          <p className="text-high">⚠ {data.forecastMessage}</p>
          <RiskBadge level={forecastRisk} />
        </div>
      </section>

      <section>
        <h2 className="mb-3 text-lg font-semibold">Attack type forecast</h2>
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {data.attackTypes.map((item, i) => (
            <AttackTypeCard key={item.type} item={item} delay={i * 50} />
          ))}
        </div>
      </section>

      <section className="grid gap-4 xl:grid-cols-5">
        <div className="glass rounded-2xl p-5 xl:col-span-3">
          <h2 className="text-lg font-semibold">Why is the AI predicting this?</h2>
          <p className="mt-1 mb-4 text-sm text-mute">Explainable factors from the detection and forecasting engines.</p>
          <ul className="space-y-3">
            {data.factors.map((f) => (
              <li key={f.id} className="flex items-center gap-3">
                <span className="flex h-8 w-8 items-center justify-center rounded-lg border border-white/10 bg-white/4">
                  {f.direction === 'up' ? <ArrowUp className="h-4 w-4 text-critical" /> : <ArrowDown className="h-4 w-4 text-safe" />}
                </span>
                <div className="min-w-0 flex-1">
                  <div className="flex items-center justify-between gap-2">
                    <p className="text-sm font-medium">{f.label}</p>
                    <p className="font-mono text-xs text-mute">Impact {f.impact}</p>
                  </div>
                  <div className="mt-1 h-1 overflow-hidden rounded-full bg-white/8">
                    <div className="h-full rounded-full bg-cyan" style={{ width: `${f.impact}%` }} />
                  </div>
                  <p className="mt-1 text-xs text-mute">{f.detail}</p>
                </div>
              </li>
            ))}
          </ul>
        </div>
        <div className="glass rounded-2xl p-5 xl:col-span-2">
          <h2 className="text-lg font-semibold">Anomaly detection</h2>
          <p className="mt-1 mb-3 text-sm text-mute">Isolation Forest score over recent windows.</p>
          <AnomalyChart data={data.anomalySeries} />
          <p className="mt-2 text-center font-mono text-[11px] text-mute">Normal → Suspicious → Anomalous → Critical</p>
        </div>
      </section>

      <section>
        <h2 className="mb-3 text-lg font-semibold">AI model pipeline</h2>
        <PipelineDiagram stages={pipelineStages} />
      </section>
    </div>
  );
}
