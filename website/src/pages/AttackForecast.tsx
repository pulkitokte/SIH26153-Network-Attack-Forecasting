import { useEffect, useState } from 'react';
import {
  Activity,
  ArrowDown,
  ArrowUp,
  ShieldAlert,
  Sparkles,
} from 'lucide-react';
import { MultiHorizonPredictionCard } from '../components/forecast/MultiHorizonPredictionCard';
import { SectionHeader } from '../components/common/SectionHeader';
import {
  explain,
  getDemoSequence,
  predict,
  type DemoSequenceResponse,
} from '../services/api';
import type {
  ExplainabilityResponse,
  MultiHorizonPrediction,
} from '../types';

const HORIZONS = [50, 100, 200, 500] as const;

function formatProbabilityDelta(delta: number): string {
  const percentagePoints = delta * 100;

  if (Math.abs(percentagePoints) < 0.01) {
    return '0.00 pp';
  }

  return `${percentagePoints > 0 ? '+' : ''}${percentagePoints.toFixed(2)} pp`;
}

function getDeltaDirection(delta: number): 'up' | 'down' | 'flat' {
  if (delta > 0.0001) {
    return 'up';
  }

  if (delta < -0.0001) {
    return 'down';
  }

  return 'flat';
}

export function AttackForecast() {
  const [prediction, setPrediction] =
    useState<MultiHorizonPrediction | null>(null);

  const [demoSequence, setDemoSequence] =
    useState<DemoSequenceResponse | null>(null);

  const [explanation, setExplanation] =
    useState<ExplainabilityResponse | null>(null);

  const [predictionError, setPredictionError] =
    useState<string | null>(null);

  const [explanationError, setExplanationError] =
    useState<string | null>(null);

  const [predictionLoading, setPredictionLoading] = useState(false);
  const [explanationLoading, setExplanationLoading] = useState(false);

  useEffect(() => {
    let cancelled = false;

    async function loadRealForecast() {
      setPredictionLoading(true);
      setPredictionError(null);
      setExplanationError(null);

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

        setExplanationLoading(true);

        const modelExplanation = await explain(
          sequenceResponse.sequence,
          67,
          96,
        );

        if (cancelled) {
          return;
        }

        setExplanation(modelExplanation);
      } catch (error) {
        if (!cancelled) {
          const message =
            error instanceof Error
              ? error.message
              : 'Unable to load real model forecast.';

          if (!prediction) {
            setPredictionError(message);
          } else {
            setExplanationError(message);
          }
        }
      } finally {
        if (!cancelled) {
          setPredictionLoading(false);
          setExplanationLoading(false);
        }
      }
    }

    void loadRealForecast();

    return () => {
      cancelled = true;
    };
  }, []);

  const attackHorizons = prediction
    ? HORIZONS.filter(
        (horizon) =>
          Number(prediction.predictions[String(horizon)]) === 1,
      )
    : [];

  const positiveHorizonCount = attackHorizons.length;

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

              <div className="min-w-0 flex-1">
                <p className="font-mono text-[11px] uppercase tracking-[0.2em] text-cyan">
                  Model Forecast Interpretation
                </p>

                <h2 className="mt-2 text-lg font-semibold">
                  {positiveHorizonCount === 4
                    ? 'Attack forecast is positive across all four horizons'
                    : positiveHorizonCount === 0
                      ? 'No forecast horizon crosses its calibrated threshold'
                      : `Attack forecast is positive at ${positiveHorizonCount} of 4 horizons`}
                </h2>

                <p className="mt-2 text-sm leading-6 text-mute">
                  The trained Multi-Horizon GRU classified the selected
                  held-out test sequence according to each horizon-specific
                  probability threshold. The result is predictive evidence,
                  not confirmation of an active attack.
                </p>

                <div className="mt-4 grid gap-3 sm:grid-cols-2">
                  <div className="rounded-xl border border-white/8 bg-white/[0.03] p-4">
                    <p className="text-[11px] uppercase tracking-wide text-mute">
                      Positive forecast horizons
                    </p>

                    <p className="mt-2 font-mono text-2xl font-semibold">
                      {positiveHorizonCount}/4
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

          <section className="glass rounded-2xl p-5">
            <div className="flex items-start gap-3">
              <div className="rounded-xl border border-cyan/20 bg-cyan/10 p-2">
                <Sparkles className="h-5 w-5 text-cyan" />
              </div>

              <div className="min-w-0 flex-1">
                <p className="font-mono text-[11px] uppercase tracking-[0.2em] text-cyan">
                  Local Model Explainability
                </p>

                <h2 className="mt-2 text-lg font-semibold">
                  Temporal feature perturbation
                </h2>

                <p className="mt-1 max-w-3xl text-sm leading-6 text-mute">
                  One observed feature at one timestep is replaced with its
                  TRAIN-only median, then the same frozen GRU is evaluated
                  again. The probability change shows local model sensitivity
                  for this specific forecast instance.
                </p>

                {explanationLoading && (
                  <div className="mt-5 rounded-xl border border-white/8 bg-white/[0.03] p-4 text-sm text-mute">
                    Running local perturbation explanation...
                  </div>
                )}

                {explanationError && (
                  <div className="mt-5 rounded-xl border border-critical/20 bg-critical/10 p-4 text-sm text-critical">
                    {explanationError}
                  </div>
                )}

                {explanation && (
                  <>
                    <div className="mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
                      <div className="rounded-xl border border-white/8 bg-white/[0.03] p-4">
                        <p className="text-[11px] uppercase tracking-wide text-mute">
                          Feature
                        </p>

                        <p className="mt-2 font-semibold">
                          {explanation.feature_name}
                        </p>

                        <p className="mt-1 font-mono text-[11px] text-mute">
                          Index {explanation.feature_index}
                        </p>
                      </div>

                      <div className="rounded-xl border border-white/8 bg-white/[0.03] p-4">
                        <p className="text-[11px] uppercase tracking-wide text-mute">
                          Observation timestep
                        </p>

                        <p className="mt-2 font-mono text-2xl font-semibold">
                          {explanation.timestep}
                        </p>

                        <p className="mt-1 text-xs text-mute">
                          Within the 100-flow observation window
                        </p>
                      </div>

                      <div className="rounded-xl border border-white/8 bg-white/[0.03] p-4">
                        <p className="text-[11px] uppercase tracking-wide text-mute">
                          Observed value
                        </p>

                        <p className="mt-2 font-mono text-lg font-semibold">
                          {explanation.original_value.toLocaleString()}
                        </p>

                        <p className="mt-1 text-xs text-mute">
                          Value used by the original forecast
                        </p>
                      </div>

                      <div className="rounded-xl border border-white/8 bg-white/[0.03] p-4">
                        <p className="text-[11px] uppercase tracking-wide text-mute">
                          TRAIN median
                        </p>

                        <p className="mt-2 font-mono text-lg font-semibold">
                          {explanation.baseline_value.toLocaleString()}
                        </p>

                        <p className="mt-1 text-xs text-mute">
                          {explanation.baseline_source}
                        </p>
                      </div>
                    </div>

                    <div className="mt-5">
                      <div className="flex items-center gap-2">
                        <Activity className="h-4 w-4 text-cyan" />

                        <p className="font-mono text-[11px] uppercase tracking-[0.18em] text-cyan">
                          Probability change after perturbation
                        </p>
                      </div>

                      <div className="mt-3 grid gap-3 sm:grid-cols-2">
                        {HORIZONS.map((horizon) => {
                          const key = String(horizon) as
                            | '50'
                            | '100'
                            | '200'
                            | '500';

                          const original =
                            explanation.original_probabilities[key];

                          const perturbed =
                            explanation.perturbed_probabilities[key];

                          const delta =
                            explanation.probability_deltas[key];

                          const direction = getDeltaDirection(delta);

                          return (
                            <div
                              key={horizon}
                              className="rounded-xl border border-white/8 bg-white/[0.03] p-4"
                            >
                              <div className="flex items-start justify-between gap-3">
                                <div>
                                  <p className="font-mono text-[11px] uppercase tracking-wide text-mute">
                                    H{horizon}
                                  </p>

                                  <p className="mt-2 font-mono text-xl font-semibold">
                                    {formatProbabilityDelta(delta)}
                                  </p>
                                </div>

                                <div className="rounded-lg border border-white/8 p-2">
                                  {direction === 'down' ? (
                                    <ArrowDown className="h-4 w-4 text-cyan" />
                                  ) : direction === 'up' ? (
                                    <ArrowUp className="h-4 w-4 text-critical" />
                                  ) : (
                                    <Activity className="h-4 w-4 text-mute" />
                                  )}
                                </div>
                              </div>

                              <div className="mt-3 grid grid-cols-2 gap-3 text-xs">
                                <div>
                                  <p className="text-mute">Original</p>
                                  <p className="mt-1 font-mono font-semibold">
                                    {(original * 100).toFixed(2)}%
                                  </p>
                                </div>

                                <div>
                                  <p className="text-mute">Perturbed</p>
                                  <p className="mt-1 font-mono font-semibold">
                                    {(perturbed * 100).toFixed(2)}%
                                  </p>
                                </div>
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    </div>

                    <div className="mt-5 rounded-xl border border-cyan/15 bg-cyan/5 p-4">
                      <p className="text-sm leading-6 text-ink">
                        {explanation.interpretation}
                      </p>

                      <p className="mt-2 text-xs leading-5 text-mute">
                        This is local model-sensitivity evidence for the
                        selected sequence. It is not a causal explanation,
                        universal feature importance score, or proof that the
                        feature caused the forecast.
                      </p>
                    </div>
                  </>
                )}
              </div>
            </div>
          </section>
        </>
      )}
    </div>
  );
}