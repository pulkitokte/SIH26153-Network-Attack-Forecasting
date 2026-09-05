import type {
  AlertItem,
  AnalyticsBundle,
  DashboardData,
  ExplainabilityResponse,
  ModelMetrics,
  MultiHorizonPrediction,
  TimeRange,
  TrafficFlow,
  TrafficPoint,
  TrafficSnapshot,
} from '../types';

import {
  buildAnalytics,
  buildTrafficFlows,
  buildTrafficSeries,
  confusionMatrix,
  datasets,
  defaultAlerts,
  defaultDashboard,
  defaultModelMetrics,
  defaultTrafficSnapshot,
  modelComparison,
  pipelineStages,
  prCurve,
  rocCurve,
} from '../data/mock';

const MOCK_LATENCY_MS = 40;

const API_BASE_URL = 'http://127.0.0.1:8000';

function wait(ms = MOCK_LATENCY_MS): Promise<void> {
  return new Promise((resolve) => {
    window.setTimeout(resolve, ms);
  });
}

/**
 * Mock API layer for the SIH dashboard.
 *
 * Existing dashboard endpoints remain mock-backed for now.
 * Real trained-model inference is available through FastAPI.
 */

export async function getDashboardData(): Promise<DashboardData> {
  await wait();
  return defaultDashboard;
}

export async function getTrafficData(): Promise<{
  snapshot: TrafficSnapshot;
  series: TrafficPoint[];
  flows: TrafficFlow[];
}> {
  await wait();
  return {
    snapshot: defaultTrafficSnapshot,
    series: buildTrafficSeries(),
    flows: buildTrafficFlows(),
  };
}

export async function getForecast(): Promise<
  Pick<
    DashboardData,
    | 'forecastSeries'
    | 'attackTypes'
    | 'factors'
    | 'attackProbability'
    | 'confidence'
    | 'predictedAttack'
    | 'forecastMessage'
    | 'forecastHorizonMin'
  >
> {
  await wait();
  const d = defaultDashboard;

  return {
    forecastSeries: d.forecastSeries,
    attackTypes: d.attackTypes,
    factors: d.factors,
    attackProbability: d.attackProbability,
    confidence: d.confidence,
    predictedAttack: d.predictedAttack,
    forecastMessage: d.forecastMessage,
    forecastHorizonMin: d.forecastHorizonMin,
  };
}

export interface DemoSequenceResponse {
  source: string;
  mode: string;
  window_id: number;
  episode_id: number;
  test_index: number;
  observation_start_position: number;
  observation_end_position: number;
  observation_length: number;
  sequence: number[][];
}

export async function getDemoSequence(): Promise<DemoSequenceResponse> {
  const response = await fetch(`${API_BASE_URL}/demo-sequence`);

  if (!response.ok) {
    const detail = await response.text();

    throw new Error(
      `Demo sequence request failed (${response.status}): ${detail}`,
    );
  }

  return response.json() as Promise<DemoSequenceResponse>;
}

export async function predict(
  sequence: number[][],
): Promise<MultiHorizonPrediction> {
  const response = await fetch(`${API_BASE_URL}/predict`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ sequence }),
  });

  if (!response.ok) {
    const detail = await response.text();

    throw new Error(
      `Prediction request failed (${response.status}): ${detail}`,
    );
  }

  return response.json() as Promise<MultiHorizonPrediction>;
}

export async function explain(
  sequence: number[][],
  featureIndex: number,
  timestep: number,
): Promise<ExplainabilityResponse> {
  const response = await fetch(`${API_BASE_URL}/explain`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      sequence,
      feature_index: featureIndex,
      timestep,
    }),
  });

  if (!response.ok) {
    const detail = await response.text();

    throw new Error(
      `Explainability request failed (${response.status}): ${detail}`,
    );
  }

  return response.json() as Promise<ExplainabilityResponse>;
}

export async function getAlerts(): Promise<AlertItem[]> {
  await wait();
  return defaultAlerts;
}

export async function getModelMetrics(): Promise<{
  metrics: ModelMetrics;
  comparison: typeof modelComparison;
  confusion: typeof confusionMatrix;
  roc: typeof rocCurve;
  pr: typeof prCurve;
}> {
  await wait();

  return {
    metrics: defaultModelMetrics,
    comparison: modelComparison,
    confusion: confusionMatrix,
    roc: rocCurve,
    pr: prCurve,
  };
}

export async function getAnalytics(
  range: TimeRange = '1h',
): Promise<AnalyticsBundle> {
  await wait();
  return buildAnalytics(range);
}

export async function getPipeline() {
  await wait();
  return pipelineStages;
}

export async function getDatasets() {
  await wait();
  return datasets;
}