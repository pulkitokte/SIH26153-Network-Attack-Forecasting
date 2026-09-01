import type {
  AlertItem,
  AnalyticsBundle,
  AnomalyPoint,
  AttackTypeForecast,
  ConfusionMatrix,
  DashboardData,
  DatasetInfo,
  ExplainabilityFactor,
  ForecastPoint,
  KpiMetric,
  ModelComparisonRow,
  ModelMetrics,
  PipelineStage,
  ProtocolShare,
  RocPoint,
  TrafficFlow,
  TrafficPoint,
  TrafficSnapshot,
} from '../types';
import { formatTimeShort } from '../utils/format';

function minutesAgo(mins: number): Date {
  return new Date(Date.now() - mins * 60_000);
}

function stamp(mins: number): string {
  return formatTimeShort(minutesAgo(mins));
}

export const MOCK_NOTE =
  'Demo / mock values for SIH presentation. Replace with live FastAPI + trained-model output.';

export const defaultKpis: KpiMetric[] = [
  {
    id: 'traffic',
    label: 'Network Traffic',
    value: '1.82M',
    unit: 'Packets/min',
    hint: 'Aggregated flow volume',
    trend: { direction: 'up', value: '+12.4%' },
    tone: 'cyan',
  },
  {
    id: 'risk',
    label: 'Current Risk',
    value: '72%',
    unit: 'High',
    hint: 'Composite network risk',
    trend: { direction: 'up', value: '+18%' },
    tone: 'amber',
  },
  {
    id: 'probability',
    label: 'Attack Probability',
    value: '78%',
    unit: 'Next 10 min',
    hint: 'Forecasting engine output',
    trend: { direction: 'up', value: '+27%' },
    tone: 'red',
  },
  {
    id: 'anomalies',
    label: 'Active Anomalies',
    value: '24',
    unit: 'Isolation Forest flags',
    hint: 'Open anomalous flows',
    trend: { direction: 'up', value: '+6' },
    tone: 'amber',
  },
  {
    id: 'horizon',
    label: 'Forecast Horizon',
    value: '10 min',
    unit: 'Predictive window',
    hint: 'LSTM/GRU lookahead',
    trend: { direction: 'flat', value: 'Stable' },
    tone: 'neutral',
  },
  {
    id: 'accuracy',
    label: 'Detection Accuracy',
    value: '94.7%',
    unit: 'Demo metric',
    hint: MOCK_NOTE,
    trend: { direction: 'up', value: '+1.1%' },
    tone: 'green',
  },
];

export const resetKpis: KpiMetric[] = [
  {
    id: 'traffic',
    label: 'Network Traffic',
    value: '0.94M',
    unit: 'Packets/min',
    hint: 'Aggregated flow volume',
    trend: { direction: 'flat', value: 'Baseline' },
    tone: 'cyan',
  },
  {
    id: 'risk',
    label: 'Current Risk',
    value: '18%',
    unit: 'Safe',
    hint: 'Composite network risk',
    trend: { direction: 'down', value: '−4%' },
    tone: 'green',
  },
  {
    id: 'probability',
    label: 'Attack Probability',
    value: '14%',
    unit: 'Next 10 min',
    hint: 'Forecasting engine output',
    trend: { direction: 'down', value: '−2%' },
    tone: 'green',
  },
  {
    id: 'anomalies',
    label: 'Active Anomalies',
    value: '3',
    unit: 'Isolation Forest flags',
    hint: 'Open anomalous flows',
    trend: { direction: 'down', value: '−1' },
    tone: 'green',
  },
  {
    id: 'horizon',
    label: 'Forecast Horizon',
    value: '10 min',
    unit: 'Predictive window',
    hint: 'LSTM/GRU lookahead',
    trend: { direction: 'flat', value: 'Stable' },
    tone: 'neutral',
  },
  {
    id: 'accuracy',
    label: 'Detection Accuracy',
    value: '94.7%',
    unit: 'Demo metric',
    hint: MOCK_NOTE,
    trend: { direction: 'flat', value: 'Held' },
    tone: 'green',
  },
];

export function buildForecastSeries(peak = 78): ForecastPoint[] {
  const historical = [18, 19, 21, 23, 26, 31, 38, 48];
  const now = Date.now();
  const points: ForecastPoint[] = historical.map((value, i) => {
    const offsetMin = (historical.length - 1 - i) * 5;
    const isNow = i === historical.length - 1;
    return {
      time: formatTimeShort(new Date(now - offsetMin * 60_000)),
      timestamp: now - offsetMin * 60_000,
      historical: value,
      forecast: isNow ? value : null,
      isNow,
    };
  });

  [58, 65, 72, peak].forEach((value, i) => {
    const mins = (i + 1) * 5;
    points.push({
      time: formatTimeShort(new Date(now + mins * 60_000)),
      timestamp: now + mins * 60_000,
      historical: null,
      forecast: value,
    });
  });

  return points;
}

export const defaultAttackTypes: AttackTypeForecast[] = [
  {
    type: 'DDoS',
    probability: 78,
    risk: 'CRITICAL',
    description: 'SYN/UDP flood signature forming across edge collectors.',
  },
  {
    type: 'Port Scan',
    probability: 42,
    risk: 'WATCH',
    description: 'Sequential destination-port probing from diverse sources.',
  },
  {
    type: 'Brute Force',
    probability: 31,
    risk: 'WATCH',
    description: 'Repeated auth attempts remain below critical threshold.',
  },
  {
    type: 'Botnet Activity',
    probability: 18,
    risk: 'SAFE',
    description: 'C2-like beaconing is present but low confidence.',
  },
];

export const defaultFactors: ExplainabilityFactor[] = [
  {
    id: 'packet-rate',
    label: 'Abnormal packet rate',
    direction: 'up',
    impact: 92,
    detail: 'Packets/min 2.4× above 1-hour baseline.',
  },
  {
    id: 'connections',
    label: 'Connection attempts',
    direction: 'up',
    impact: 84,
    detail: 'New TCP handshakes clustering on a short window.',
  },
  {
    id: 'syn',
    label: 'SYN traffic',
    direction: 'up',
    impact: 88,
    detail: 'Half-open SYN ratio exceeding Isolation Forest threshold.',
  },
  {
    id: 'diversity',
    label: 'Source IP diversity',
    direction: 'up',
    impact: 76,
    detail: 'Unique source entropy inconsistent with normal enterprise traffic.',
  },
  {
    id: 'anomaly',
    label: 'Network anomaly score',
    direction: 'up',
    impact: 91,
    detail: 'Rolling Isolation Forest score entering the critical band.',
  },
];

export const defaultAnomalySeries: AnomalyPoint[] = [
  { time: stamp(20), score: 0.12, label: 'Normal' },
  { time: stamp(16), score: 0.18, label: 'Normal' },
  { time: stamp(12), score: 0.29, label: 'Normal' },
  { time: stamp(8), score: 0.54, label: 'Suspicious' },
  { time: stamp(4), score: 0.81, label: 'Anomalous' },
  { time: stamp(0), score: 0.93, label: 'Critical' },
];

export const defaultDashboard: DashboardData = {
  kpis: defaultKpis,
  attackProbability: 78,
  currentRisk: 72,
  packetsPerMin: 1_820_000,
  activeAnomalies: 24,
  forecastHorizonMin: 10,
  detectionAccuracy: 94.7,
  predictedAttack: 'DDoS',
  confidence: 91,
  forecastMessage: 'High probability of DDoS activity detected in the forecast window.',
  forecastSeries: buildForecastSeries(78),
  attackTypes: defaultAttackTypes,
  factors: defaultFactors,
  anomalySeries: defaultAnomalySeries,
  engineOnline: true,
};

export const resetDashboard: DashboardData = {
  kpis: resetKpis,
  attackProbability: 14,
  currentRisk: 18,
  packetsPerMin: 940_000,
  activeAnomalies: 3,
  forecastHorizonMin: 10,
  detectionAccuracy: 94.7,
  predictedAttack: 'DDoS',
  confidence: 71,
  forecastMessage: 'No material attack forecast in the current window.',
  forecastSeries: buildForecastSeries(18).map((point, i) => ({
    ...point,
    historical: point.historical == null ? null : 11 + i,
    forecast: point.forecast == null ? null : 14 + Math.max(0, i - 7),
  })),
  attackTypes: defaultAttackTypes.map((item) => ({
    ...item,
    probability: Math.max(6, Math.round(item.probability * 0.22)),
    risk: 'SAFE',
  })),
  factors: defaultFactors.map((f) => ({ ...f, impact: Math.round(f.impact * 0.28), direction: 'down' })),
  anomalySeries: [
    { time: stamp(20), score: 0.1, label: 'Normal' },
    { time: stamp(16), score: 0.12, label: 'Normal' },
    { time: stamp(12), score: 0.11, label: 'Normal' },
    { time: stamp(8), score: 0.14, label: 'Normal' },
    { time: stamp(4), score: 0.16, label: 'Normal' },
    { time: stamp(0), score: 0.13, label: 'Normal' },
  ],
  engineOnline: true,
};

export const defaultProtocols: ProtocolShare[] = [
  { protocol: 'TCP', value: 38, packets: 690_000 },
  { protocol: 'HTTPS', value: 24, packets: 436_000 },
  { protocol: 'UDP', value: 16, packets: 291_000 },
  { protocol: 'HTTP', value: 9, packets: 164_000 },
  { protocol: 'DNS', value: 8, packets: 145_000 },
  { protocol: 'ICMP', value: 5, packets: 91_000 },
];

export const defaultTrafficSnapshot: TrafficSnapshot = {
  packetsPerSec: 30_400,
  bytesPerSec: 18_400_000,
  activeConnections: 4_218,
  anomalyScore: 0.81,
  networkRisk: 72,
  protocolDistribution: defaultProtocols,
};

export function buildTrafficSeries(count = 24, scale = 1): TrafficPoint[] {
  return Array.from({ length: count }, (_, i) => {
    const t = new Date(Date.now() - (count - 1 - i) * 5_000);
    const wave = Math.sin(i / 3.2) * 0.12 + 1;
    return {
      time: t.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
      timestamp: t.getTime(),
      packets: Math.round(28_000 * wave * scale),
      bytes: Math.round(16_000_000 * wave * scale),
      anomaly: Math.min(0.98, 0.18 * scale + i * 0.015 * scale),
    };
  });
}

const PRIVATE_SOURCES = ['192.168.1.10', '192.168.1.24', '10.0.0.24', '10.0.4.18', '172.16.0.15', '172.16.8.41'];
const PRIVATE_DESTS = ['10.0.0.8', '192.168.1.1', '172.16.0.1', '10.20.0.5', '192.168.50.12'];
const PROTOCOLS = ['TCP', 'UDP', 'HTTP', 'HTTPS', 'DNS', 'ICMP'] as const;

export function buildTrafficFlows(count = 18, anomalyBoost = 0.7): TrafficFlow[] {
  return Array.from({ length: count }, (_, i) => {
    const score = Math.min(0.99, Math.abs(Math.sin(i * 1.3)) * anomalyBoost + (i % 5 === 0 ? 0.35 : 0.08));
    const status =
      score > 0.85 ? 'Critical' : score > 0.65 ? 'Anomalous' : score > 0.4 ? 'Suspicious' : 'Normal';
    const t = new Date(Date.now() - i * 7_000);
    return {
      id: `flow-${i}-${t.getTime()}`,
      time: t.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
      sourceIp: PRIVATE_SOURCES[i % PRIVATE_SOURCES.length],
      destinationIp: PRIVATE_DESTS[i % PRIVATE_DESTS.length],
      protocol: PROTOCOLS[i % PROTOCOLS.length],
      packets: 120 + i * 37 + Math.round(score * 800),
      bytes: 8_400 + i * 910 + Math.round(score * 12_000),
      anomalyScore: Number(score.toFixed(2)),
      status,
    };
  });
}

export const defaultAlerts: AlertItem[] = [
  {
    id: 'alert-1',
    timestamp: stamp(2),
    severity: 'CRITICAL',
    title: 'Possible DDoS attack predicted',
    threatType: 'DDoS',
    probability: 87,
    forecastWindow: 'Next 8 minutes',
    status: 'ACTIVE',
    recommendedAction: 'Enable SYN cookies, rate-limit edge UDP, and notify the on-call SOC analyst.',
  },
  {
    id: 'alert-2',
    timestamp: stamp(11),
    severity: 'HIGH',
    title: 'Port scanning activity increasing',
    threatType: 'Port Scan',
    probability: 64,
    forecastWindow: 'Next 18 minutes',
    status: 'ACTIVE',
    recommendedAction: 'Review firewall logs for sequential port probes and tighten unused service exposure.',
  },
  {
    id: 'alert-3',
    timestamp: stamp(27),
    severity: 'MEDIUM',
    title: 'Abnormal DNS traffic detected',
    threatType: 'DNS',
    probability: 42,
    forecastWindow: 'Next 25 minutes',
    status: 'ACKNOWLEDGED',
    recommendedAction: 'Inspect DNS query entropy and block suspicious resolvers if beaconing persists.',
  },
  {
    id: 'alert-4',
    timestamp: stamp(48),
    severity: 'LOW',
    title: 'Traffic anomaly resolved',
    threatType: 'Anomaly',
    probability: 12,
    forecastWindow: 'Closed',
    status: 'RESOLVED',
    recommendedAction: 'No action required. Keep the forecasting engine on live monitoring.',
  },
  {
    id: 'alert-5',
    timestamp: stamp(63),
    severity: 'MEDIUM',
    title: 'Brute-force pattern forming on auth edge',
    threatType: 'Brute Force',
    probability: 38,
    forecastWindow: 'Next 30 minutes',
    status: 'ACKNOWLEDGED',
    recommendedAction: 'Apply progressive backoff and lockout on the affected identity provider.',
  },
];

export const defaultModelMetrics: ModelMetrics = {
  accuracy: 94.7,
  precision: 93.2,
  recall: 91.8,
  f1: 92.5,
  rocAuc: 95.1,
  demoNote: MOCK_NOTE,
};

export const modelComparison: ModelComparisonRow[] = [
  { model: 'Isolation Forest', accuracy: 89.2, f1: 87.8, role: 'Anomaly detection layer' },
  { model: 'GRU', accuracy: 92.6, f1: 91.3, role: 'Sequence forecasting' },
  { model: 'LSTM', accuracy: 94.7, f1: 92.5, role: 'Primary forecasting engine' },
];

export const confusionMatrix: ConfusionMatrix = {
  labels: ['Benign', 'Attack'],
  values: [
    [912, 48],
    [61, 879],
  ],
};

export const rocCurve: RocPoint[] = [
  { fpr: 0, tpr: 0 },
  { fpr: 0.02, tpr: 0.41 },
  { fpr: 0.05, tpr: 0.68 },
  { fpr: 0.08, tpr: 0.81 },
  { fpr: 0.12, tpr: 0.89 },
  { fpr: 0.18, tpr: 0.93 },
  { fpr: 0.28, tpr: 0.96 },
  { fpr: 0.45, tpr: 0.98 },
  { fpr: 1, tpr: 1 },
];

export const prCurve: RocPoint[] = [
  { fpr: 0.12, tpr: 1 },
  { fpr: 0.35, tpr: 0.98 },
  { fpr: 0.52, tpr: 0.96 },
  { fpr: 0.68, tpr: 0.94 },
  { fpr: 0.8, tpr: 0.91 },
  { fpr: 0.9, tpr: 0.84 },
  { fpr: 0.97, tpr: 0.62 },
  { fpr: 1, tpr: 0.2 },
];

export const datasets: DatasetInfo[] = [
  {
    name: 'CICIDS2017',
    trafficType: 'PCAP / flow features, 5-day capture',
    attackCategories: 'DoS, DDoS, brute force, Heartbleed, botnet, web, infiltration',
    records: '2.8M flows (placeholder)',
    status: 'Loaded',
    note: 'Primary training corpus for flow-level features.',
  },
  {
    name: 'CICIDS2018',
    trafficType: 'AWS-captured enterprise traffic',
    attackCategories: 'DoS, DDoS, brute force, botnet, infiltration, web attacks',
    records: '8.1M flows (placeholder)',
    status: 'Indexed',
    note: 'Used for temporal generalization checks.',
  },
  {
    name: 'NSL-KDD',
    trafficType: 'Connection records, benchmark IDS set',
    attackCategories: 'DoS, Probe, R2L, U2R',
    records: '148K records (placeholder)',
    status: 'Ready',
    note: 'Baseline comparison dataset. Not used as the sole production source.',
  },
  {
    name: 'UNSW-NB15',
    trafficType: 'Synthetic + real hybrid traces',
    attackCategories: 'Fuzzers, analysis, backdoors, DoS, exploits, generic, reconnaissance, shellcode, worms',
    records: '2.5M records (placeholder)',
    status: 'Ready',
    note: 'Supports multi-class threat-vector experiments.',
  },
];

export const pipelineStages: PipelineStage[] = [
  {
    id: 'traffic',
    title: 'Network Traffic',
    description: 'Flow duration, packet count, byte rate, protocol, flags',
  },
  {
    id: 'features',
    title: 'Feature Engineering',
    description: 'Windowed stats, entropy, SYN ratio, source diversity',
  },
  {
    id: 'iforest',
    title: 'Anomaly Detection',
    description: 'Isolation Forest identifies abnormal traffic patterns',
  },
  {
    id: 'window',
    title: 'Time-Series Windowing',
    description: 'Sliding windows convert scores into sequential tensors',
  },
  {
    id: 'forecast',
    title: 'LSTM / GRU Forecasting',
    description: 'Learns temporal attack patterns from anomaly trajectories',
  },
  {
    id: 'probability',
    title: 'Attack Probability',
    description: 'Probability of attack in the next X minutes',
  },
  {
    id: 'alert',
    title: 'Risk Alert',
    description: 'Predictive SOC alert with confidence and recommended action',
  },
];

export function buildAnalytics(range: '15m' | '1h' | '6h' | '24h' = '1h'): AnalyticsBundle {
  const points = range === '15m' ? 15 : range === '1h' ? 12 : range === '6h' ? 12 : 24;
  const stepMs = range === '15m' ? 60_000 : range === '1h' ? 5 * 60_000 : range === '6h' ? 30 * 60_000 : 60 * 60_000;

  return {
    attackDistribution: [
      { name: 'DDoS', value: 41 },
      { name: 'Port Scan', value: 22 },
      { name: 'Brute Force', value: 16 },
      { name: 'Botnet', value: 12 },
      { name: 'Other', value: 9 },
    ],
    trafficVolume: Array.from({ length: points }, (_, i) => {
      const t = new Date(Date.now() - (points - 1 - i) * stepMs);
      return {
        time: range === '24h' ? `${t.getHours().toString().padStart(2, '0')}:00` : formatTimeShort(t),
        volume: Math.round(0.8 + Math.abs(Math.sin(i / 2.4)) * 1.4 + i * 0.02) * 100_000,
      };
    }),
    anomalyTrend: Array.from({ length: points }, (_, i) => ({
      time: formatTimeShort(new Date(Date.now() - (points - 1 - i) * stepMs)),
      score: Number((0.12 + i * (0.7 / points) + Math.sin(i) * 0.04).toFixed(2)),
    })),
    probabilityTrend: Array.from({ length: points }, (_, i) => ({
      time: formatTimeShort(new Date(Date.now() - (points - 1 - i) * stepMs)),
      probability: Math.round(18 + i * (60 / points) + Math.cos(i / 2) * 4),
    })),
    protocolDistribution: defaultProtocols,
    hourlyHeatmap: Array.from({ length: 24 }, (_, hour) => ({
      hour: `${hour.toString().padStart(2, '0')}:00`,
      risk: Math.round(12 + Math.abs(Math.sin(hour / 3.1)) * 70 + (hour > 16 ? 8 : 0)),
    })),
  };
}
