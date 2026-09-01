import type { AlertItem, AnalyticsBundle, DashboardData, ModelMetrics, TimeRange, TrafficFlow, TrafficPoint, TrafficSnapshot } from '../types';
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

function wait(ms = MOCK_LATENCY_MS): Promise<void> {
  return new Promise((resolve) => {
    window.setTimeout(resolve, ms);
  });
}

/**
 * Mock API layer for the SIH dashboard.
 * Swap these implementations with FastAPI fetches:
 *   GET /dashboard  GET /traffic  GET /forecast  GET /alerts  GET /metrics  POST /predict
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

export async function getForecast(): Promise<Pick<DashboardData, 'forecastSeries' | 'attackTypes' | 'factors' | 'attackProbability' | 'confidence' | 'predictedAttack' | 'forecastMessage' | 'forecastHorizonMin'>> {
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

export async function getAnalytics(range: TimeRange = '1h'): Promise<AnalyticsBundle> {
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
