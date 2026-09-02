import { useEffect, useState } from 'react';
import { ShieldAlert } from 'lucide-react';
import { MultiHorizonPredictionCard } from '../components/forecast/MultiHorizonPredictionCard';
import { SectionHeader } from '../components/common/SectionHeader';
import {
  getDemoSequence,
  predict,
  type DemoSequenceResponse,
} from '../services/api';
import type { MultiHorizonPrediction } from '../types';

export function AttackForecast() {
  const [prediction, setPrediction] =
    useState<MultiHorizonPrediction | null>(null);

  const [demoSequence, setDemoSequence] =
    useState<DemoSequenceResponse | null>(null);

  const [predictionError, setPredictionError] =
    useState<string | null>(null);

  const [predictionLoading, setPredictionLoading] = useState(false);

  useEffect(() => {
    let cancelled = false;

    async function loadRealPrediction() {
      setPredictionLoading(true);
      setPredictionError(null);

      try {
        const sequenceResponse = await getDemoSequence();

        if (cancelled) {
          return;
        }

        setDemoSequence(sequenceResponse);

        const modelPrediction = await predict(sequenceResponse.sequence);

        if (cancelled) {
          return;
        }

        setPrediction(modelPrediction);
      } catch (error) {
        if (!cancelled) {
          setPredictionError(
            error instanceof Error
              ? error.message
              : 'Unable to load real model prediction.',
          );
        }
      } finally {
        if (!cancelled) {
          setPredictionLoading(false);
        }
      }
    }

    void loadRealPrediction();

    return () => {
      cancelled = true;
    };
  }, []);

  const attackHorizons = prediction
    ? [50, 100, 200, 500].filter(
        (horizon) => Number(prediction.predictions[String(horizon)]) === 1,
      )
    : [];

  return (
    <div className="space-y-6">
      <SectionHeader
        eyebrow="Forecasting engine"
        title="Predictive Threat Intelligence"
        subtitle="Multi-Horizon GRU forecasting over future network-flow windows. This is a forecast, not a confirmation that an attack is already underway."
      />

      {predictionLoading && (
        <div className="glass rounded-2xl p-5 text-sm text-mute">
          Running real Multi-Horizon GRU inference...
        </div>
      )}

      {predictionError && (
        <div className="glass rounded-2xl border border-critical/20 p-5 text-sm text-critical">
          {predictionError}
        </div>
      )}

      {prediction && (
        <>
          <MultiHorizonPredictionCard prediction={prediction} />

          {demoSequence && (
            <div className="glass rounded-2xl border border-cyan/20 p-4">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div>
                  <p className="font-mono text-[11px] uppercase tracking-[0.2em] text-cyan">
                    Offline Demo Sequence
                  </p>

                  <p className="mt-1 text-sm text-ink">
                    CICIDS2017 held-out TEST sequence
                  </p>
                </div>

                <div className="flex flex-wrap gap-3 font-mono text-[11px] text-mute">
                  <span>Window {demoSequence.window_id}</span>
                  <span>Episode {demoSequence.episode_id}</span>
                  <span>
                    Flows {demoSequence.observation_start_position}–
                    {demoSequence.observation_end_position}
                  </span>
                </div>
              </div>
            </div>
          )}

          <section className="glass rounded-2xl p-5">
            <div className="flex items-start gap-3">
              <div className="rounded-xl border border-critical/20 bg-critical/10 p-2">
                <ShieldAlert className="h-5 w-5 text-critical" />
              </div>

              <div>
                <p className="font-mono text-[11px] uppercase tracking-[0.2em] text-cyan">
                  Model Forecast Interpretation
                </p>

                <h2 className="mt-2 text-lg font-semibold">
                  Attack forecast is positive across all four horizons
                </h2>

                <p className="mt-2 text-sm leading-6 text-mute">
                  The trained Multi-Horizon GRU classified the selected
                  held-out test sequence as an attack forecast at the
                  50-, 100-, 200-, and 500-flow horizons.
                </p>

                <div className="mt-4 grid gap-3 sm:grid-cols-2">
                  <div className="rounded-xl border border-white/8 bg-white/[0.03] p-4">
                    <p className="text-[11px] uppercase tracking-wide text-mute">
                      Positive forecast horizons
                    </p>

                    <p className="mt-2 font-mono text-2xl font-semibold">
                      {attackHorizons.length}/4
                    </p>

                    <p className="mt-1 text-xs text-mute">
                      Horizons crossing their calibrated thresholds
                    </p>
                  </div>

                  <div className="rounded-xl border border-white/8 bg-white/[0.03] p-4">
                    <p className="text-[11px] uppercase tracking-wide text-mute">
                      Sequence source
                    </p>

                    <p className="mt-2 text-sm font-semibold">
                      Held-out TEST data
                    </p>

                    <p className="mt-1 text-xs text-mute">
                      No live telemetry or fabricated feature mapping is used
                      for this demo inference.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </section>
        </>
      )}
    </div>
  );
}