export type RiskLevel = 'SAFE' | 'WATCH' | 'HIGH' | 'CRITICAL';
export type AlertSeverity = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
export type AlertStatus = 'ACTIVE' | 'ACKNOWLEDGED' | 'RESOLVED';
export type Protocol = 'TCP' | 'UDP' | 'HTTP' | 'HTTPS' | 'DNS' | 'ICMP';
export type AttackType = 'DDoS' | 'Port Scan' | 'Brute Force' | 'Botnet Activity' | 'Other';
export type SimulationMode = 'default' | 'running' | 'stopped' | 'reset';
export type TimeRange = '15m' | '1h' | '6h' | '24h';
export type DatasetStatus = 'Loaded' | 'Indexed' | 'Ready' | 'Pending';

export interface Trend {
  direction: 'up' | 'down' | 'flat';
  value: string;
}

export interface KpiMetric {
  id: string;
  label: string;
  value: string;
  unit: string;
  hint: string;
  trend: Trend;
  tone: 'cyan' | 'amber' | 'red' | 'green' | 'neutral';
}

export interface ForecastPoint {
  time: string;
  timestamp: number;
  historical: number | null;
  forecast: number | null;
  isNow?: boolean;
}

export interface AttackTypeForecast {
  type: AttackType;
  probability: number;
  risk: RiskLevel;
  description: string;
}

export interface ExplainabilityFactor {
  id: string;
  label: string;
  direction: 'up' | 'down';
  impact: number;
  detail: string;
}

export interface TrafficSnapshot {
  packetsPerSec: number;
  bytesPerSec: number;
  activeConnections: number;
  anomalyScore: number;
  networkRisk: number;
  protocolDistribution: ProtocolShare[];
}

export interface ProtocolShare {
  protocol: Protocol;
  value: number;
  packets: number;
}

export interface TrafficPoint {
  time: string;
  timestamp: number;
  packets: number;
  bytes: number;
  anomaly: number;
}

export interface TrafficFlow {
  id: string;
  time: string;
  sourceIp: string;
  destinationIp: string;
  protocol: Protocol;
  packets: number;
  bytes: number;
  anomalyScore: number;
  status: 'Normal' | 'Suspicious' | 'Anomalous' | 'Critical';
}

export interface AlertItem {
  id: string;
  timestamp: string;
  severity: AlertSeverity;
  title: string;
  threatType: AttackType | 'Anomaly' | 'DNS';
  probability: number;
  forecastWindow: string;
  status: AlertStatus;
  recommendedAction: string;
  simulated?: boolean;
}

export interface AnomalyPoint {
  time: string;
  score: number;
  label: 'Normal' | 'Suspicious' | 'Anomalous' | 'Critical';
}

export interface ModelMetrics {
  accuracy: number;
  precision: number;
  recall: number;
  f1: number;
  rocAuc: number;
  demoNote: string;
}

export interface MultiHorizonPrediction {
  probabilities: Record<string, number>;
  thresholds: Record<string, number>;
  predictions: Record<string, number>;
}

export type ForecastHorizon = '50' | '100' | '200' | '500';

export interface ExplainabilityResponse {
  method: string;
  interpretation: string;
  feature_index: number;
  feature_name: string;
  timestep: number;
  original_value: number;
  baseline_value: number;
  baseline_source: string;
  original_probabilities: Record<ForecastHorizon, number>;
  perturbed_probabilities: Record<ForecastHorizon, number>;
  probability_deltas: Record<ForecastHorizon, number>;
  absolute_probability_deltas: Record<ForecastHorizon, number>;
  thresholds: Record<ForecastHorizon, number>;
  predictions: Record<ForecastHorizon, number>;
}

export interface ModelComparisonRow {
  model: string;
  accuracy: number;
  f1: number;
  role: string;
}

export interface ConfusionMatrix {
  labels: [string, string];
  values: [[number, number], [number, number]];
}

export interface RocPoint {
  fpr: number;
  tpr: number;
}

export interface DatasetInfo {
  name: string;
  trafficType: string;
  attackCategories: string;
  records: string;
  status: DatasetStatus;
  note: string;
}

export interface PipelineStage {
  id: string;
  title: string;
  description: string;
}

export interface DashboardData {
  kpis: KpiMetric[];
  attackProbability: number;
  currentRisk: number;
  packetsPerMin: number;
  activeAnomalies: number;
  forecastHorizonMin: number;
  detectionAccuracy: number;
  predictedAttack: AttackType;
  confidence: number;
  forecastMessage: string;
  forecastSeries: ForecastPoint[];
  attackTypes: AttackTypeForecast[];
  factors: ExplainabilityFactor[];
  anomalySeries: AnomalyPoint[];
  engineOnline: boolean;
}

export interface AnalyticsBundle {
  attackDistribution: { name: string; value: number }[];
  trafficVolume: { time: string; volume: number }[];
  anomalyTrend: { time: string; score: number }[];
  probabilityTrend: { time: string; probability: number }[];
  protocolDistribution: ProtocolShare[];
  hourlyHeatmap: { hour: string; risk: number }[];
}