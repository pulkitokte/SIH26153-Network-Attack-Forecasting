import { ArrowDown, ArrowUp } from 'lucide-react';
import { PredictionCard } from '../components/forecast/PredictionCard';
import { ForecastChart } from '../components/forecast/ForecastChart';
import { AttackTypeCard } from '../components/forecast/AttackTypeCard';
import { SectionHeader } from '../components/common/SectionHeader';
import { useSimulation } from '../context/SimulationContext';
import { getRiskLevel } from '../utils/risk';

export function AttackForecast() {
  const { data } = useSimulation();
  return (
    <div className="space-y-6">
      <SectionHeader
        eyebrow="Forecasting engine"
        title="Predictive Threat Intelligence"
        subtitle="LSTM/GRU output over the near-term horizon. This is a forecast, not a confirmation that an attack is already underway."
      />
      <div className="grid gap-4 xl:grid-cols-5">
        <div className="xl:col-span-2">
          <PredictionCard
            probability={data.attackProbability}
            predictedAttack={data.predictedAttack}
            confidence={data.confidence}
            horizon={data.forecastHorizonMin}
            risk={getRiskLevel(data.attackProbability)}
          />
        </div>
        <div className="glass rounded-2xl p-5 xl:col-span-3">
          <div className="mb-3 flex items-center justify-between">
            <h2 className="text-sm font-semibold">Attack probability over time</h2>
            <p className="font-mono text-[11px] text-cyan">Forecast: Next {data.forecastHorizonMin} Minutes</p>
          </div>
          <ForecastChart data={data.forecastSeries} />
        </div>
      </div>
      <section className="glass rounded-2xl p-5">
        <h2 className="text-lg font-semibold">Why is the AI predicting this?</h2>
        <p className="mt-1 mb-4 text-sm text-mute">
          Feature contributions from the Isolation Forest layer and temporal model. Judges should read this as model rationale, not ground truth.
        </p>
        <div className="grid gap-3 md:grid-cols-2">
          {data.factors.map((f) => (
            <div key={f.id} className="rounded-xl border border-white/8 bg-white/[0.03] p-4">
              <div className="flex items-center justify-between gap-2">
                <p className="flex items-center gap-2 text-sm font-medium">
                  {f.direction === 'up' ? <ArrowUp className="h-4 w-4 text-critical" /> : <ArrowDown className="h-4 w-4 text-safe" />}
                  {f.label}
                </p>
                <span className="font-mono text-xs text-mute">{f.impact}</span>
              </div>
              <div className="mt-2 h-1.5 overflow-hidden rounded-full bg-white/8">
                <div className="h-full rounded-full bg-cyan" style={{ width: `${f.impact}%` }} />
              </div>
              <p className="mt-2 text-xs text-mute">{f.detail}</p>
            </div>
          ))}
        </div>
      </section>
      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {data.attackTypes.map((item) => (
          <AttackTypeCard key={item.type} item={item} />
        ))}
      </section>
    </div>
  );
}
