import type { MultiHorizonPrediction, RiskLevel } from '../../types';
import { RiskBadge } from '../common/RiskBadge';
import { getRiskLevel } from '../../utils/risk';

const HORIZONS = [50, 100, 200, 500] as const;

function getProbability(
  prediction: MultiHorizonPrediction,
  horizon: number,
): number {
  return Number(prediction.probabilities[String(horizon)] ?? 0);
}

function getThreshold(
  prediction: MultiHorizonPrediction,
  horizon: number,
): number {
  return Number(prediction.thresholds[String(horizon)] ?? 0);
}

function getPrediction(
  prediction: MultiHorizonPrediction,
  horizon: number,
): number {
  return Number(prediction.predictions[String(horizon)] ?? 0);
}

function getRisk(probability: number): RiskLevel {
  return getRiskLevel(probability * 100);
}

export function MultiHorizonPredictionCard({
  prediction,
}: {
  prediction: MultiHorizonPrediction;
}) {
  return (
    <article className="glass rounded-2xl p-6">
      <div className="mb-5">
        <p className="font-mono text-[11px] uppercase tracking-[0.2em] text-mute">
          Real Multi-Horizon GRU Output
        </p>
        <h2 className="mt-2 text-lg font-semibold">
          Attack probability by forecast horizon
        </h2>
        <p className="mt-1 text-xs text-mute">
          Probabilities are produced by the trained model through the FastAPI
          inference endpoint.
        </p>
      </div>

      <div className="grid gap-3 sm:grid-cols-2">
        {HORIZONS.map((horizon) => {
          const probability = getProbability(prediction, horizon);
          const threshold = getThreshold(prediction, horizon);
          const predicted = getPrediction(prediction, horizon);
          const probabilityPercent = probability * 100;
          const thresholdPercent = threshold * 100;
          const risk = getRisk(probability);

          return (
            <div
              key={horizon}
              className="rounded-xl border border-white/8 bg-white/[0.03] p-4"
            >
              <div className="flex items-start justify-between gap-3">
                <div>
                  <p className="font-mono text-[11px] uppercase tracking-wide text-mute">
                    Next {horizon} flows
                  </p>
                  <p className="mt-2 font-mono text-3xl font-semibold">
                    {probabilityPercent.toFixed(1)}%
                  </p>
                </div>

                <RiskBadge level={risk} />
              </div>

              <div className="mt-3 h-1.5 overflow-hidden rounded-full bg-white/8">
                <div
                  className="h-full rounded-full bg-cyan"
                  style={{
                    width: `${Math.min(probabilityPercent, 100)}%`,
                  }}
                />
              </div>

              <div className="mt-4 grid grid-cols-2 gap-3 text-xs">
                <div>
                  <p className="text-mute">Threshold</p>
                  <p className="mt-1 font-mono font-semibold">
                    {thresholdPercent.toFixed(1)}%
                  </p>
                </div>

                <div>
                  <p className="text-mute">Prediction</p>
                  <p className="mt-1 font-mono font-semibold">
                    {predicted === 1 ? 'ATTACK' : 'NO ATTACK'}
                  </p>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </article>
  );
}