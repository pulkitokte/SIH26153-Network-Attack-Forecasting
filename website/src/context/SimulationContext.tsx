import { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState, type ReactNode } from 'react';
import type { AlertItem, DashboardData, SimulationMode, TrafficFlow, TrafficPoint, TrafficSnapshot } from '../types';
import { defaultAlerts, defaultDashboard, resetDashboard, buildForecastSeries, buildTrafficFlows, buildTrafficSeries } from '../data/mock';
import { clamp, easeInOut, getAnomalyLabel, getRiskLevel, lerp } from '../utils/risk';
import { formatCompact, formatClock } from '../utils/format';
import { getAlerts, getDashboardData } from '../services/api';

const SIM_DURATION_MS = 20_000;

export interface SimulationSnapshot {
  mode: SimulationMode;
  data: DashboardData;
  snapshot: TrafficSnapshot;
  series: TrafficPoint[];
  flows: TrafficFlow[];
  alerts: AlertItem[];
  banner: string | null;
  lastUpdated: string;
  progress: number;
  start: () => void;
  stop: () => void;
  reset: () => void;
}

const SimulationContext = createContext<SimulationSnapshot | null>(null);

function scaleDashboard(base: DashboardData, t: number): DashboardData {
  const e = easeInOut(t);
  const attackProbability = lerp(14, 91, e);
  const currentRisk = lerp(18, 88, e);
  const packetsPerMin = lerp(940_000, 2_450_000, e);
  const activeAnomalies = Math.round(lerp(3, 36, e));
  const forecastHorizonMin = Math.round(lerp(12, 8, e));
  const confidence = Math.round(lerp(74, 93, e));
  const anomalyNow = lerp(0.13, 0.94, e);
  const predictedAttack = attackProbability > 40 ? 'DDoS' : base.predictedAttack;

  const kpis = base.kpis.map((kpi) => {
    if (kpi.id === 'traffic') {
      return { ...kpi, value: formatCompact(packetsPerMin), trend: { direction: 'up' as const, value: `+${Math.round(e * 86)}%` }, tone: 'cyan' as const };
    }
    if (kpi.id === 'risk') {
      const level = getRiskLevel(currentRisk);
      return { ...kpi, value: `${Math.round(currentRisk)}%`, unit: level[0] + level.slice(1).toLowerCase(), trend: { direction: 'up' as const, value: `+${Math.round(e * 70)}%` }, tone: currentRisk > 80 ? 'red' as const : currentRisk > 60 ? 'amber' as const : 'green' as const };
    }
    if (kpi.id === 'probability') {
      return { ...kpi, value: `${Math.round(attackProbability)}%`, unit: `Next ${forecastHorizonMin} min`, trend: { direction: 'up' as const, value: `+${Math.round(e * 77)}%` }, tone: attackProbability > 80 ? 'red' as const : 'amber' as const };
    }
    if (kpi.id === 'anomalies') {
      return { ...kpi, value: String(activeAnomalies), trend: { direction: 'up' as const, value: `+${activeAnomalies - 3}` }, tone: 'amber' as const };
    }
    if (kpi.id === 'horizon') {
      return { ...kpi, value: `${forecastHorizonMin} min` };
    }
    return kpi;
  });

  const attackTypes = base.attackTypes.map((item) => {
    const probability =
      item.type === 'DDoS'
        ? Math.round(lerp(12, 91, e))
        : item.type === 'Port Scan'
          ? Math.round(lerp(10, 48, e))
          : item.type === 'Brute Force'
            ? Math.round(lerp(8, 34, e))
            : Math.round(lerp(6, 22, e));
    return { ...item, probability, risk: getRiskLevel(probability) };
  });

  const factors = base.factors.map((f) => ({
    ...f,
    direction: 'up' as const,
    impact: Math.round(lerp(22, f.id === 'syn' || f.id === 'packet-rate' ? 94 : 86, e)),
  }));

  const anomalySeries = [0.1, 0.12, 0.16, 0.28, 0.46, 0.63, 0.81, anomalyNow].map((score, i) => ({
    time: formatClock(new Date(Date.now() - (7 - i) * 40_000)).slice(0, 5),
    score: Number(score.toFixed(2)),
    label: getAnomalyLabel(score),
  }));

  const peak = Math.round(attackProbability);
  const series = buildForecastSeries(peak).map((point, i, arr) => {
    const nowIndex = arr.findIndex((p) => p.isNow);
    if (point.historical != null) {
      const hist = lerp(12, 18 + i * 4, e);
      return { ...point, historical: Math.round(hist), forecast: point.isNow ? Math.round(hist) : null };
    }
    const step = i - nowIndex;
    return { ...point, forecast: Math.round(lerp(16, 18 + step * 14, e) + (step === 4 ? peak - 72 : 0)) };
  });

  const forecastMessage =
    attackProbability >= 61
      ? `Potential DDoS attack predicted in approximately ${forecastHorizonMin} minutes.`
      : attackProbability >= 31
        ? 'Watch: attack probability is climbing inside the forecast window.'
        : 'No material attack forecast in the current window.';

  return {
    ...base,
    kpis,
    attackProbability: Math.round(attackProbability),
    currentRisk: Math.round(currentRisk),
    packetsPerMin,
    activeAnomalies,
    forecastHorizonMin,
    confidence,
    predictedAttack,
    forecastMessage,
    forecastSeries: series,
    attackTypes,
    factors,
    anomalySeries,
  };
}

function snapshotFrom(data: DashboardData, t: number): TrafficSnapshot {
  const e = easeInOut(t);
  return {
    packetsPerSec: Math.round(lerp(15_200, 48_800, e)),
    bytesPerSec: Math.round(lerp(8_200_000, 31_000_000, e)),
    activeConnections: Math.round(lerp(1_840, 9_420, e)),
    anomalyScore: Number(lerp(0.13, 0.94, e).toFixed(2)),
    networkRisk: data.currentRisk,
    protocolDistribution: data.kpis
      ? [
          { protocol: 'TCP', value: Math.round(lerp(28, 46, e)), packets: Math.round(data.packetsPerMin * 0.4) },
          { protocol: 'UDP', value: Math.round(lerp(12, 22, e)), packets: Math.round(data.packetsPerMin * 0.18) },
          { protocol: 'HTTPS', value: Math.round(lerp(30, 16, e)), packets: Math.round(data.packetsPerMin * 0.2) },
          { protocol: 'HTTP', value: 8, packets: Math.round(data.packetsPerMin * 0.08) },
          { protocol: 'DNS', value: Math.round(lerp(10, 6, e)), packets: Math.round(data.packetsPerMin * 0.08) },
          { protocol: 'ICMP', value: Math.round(lerp(4, 8, e)), packets: Math.round(data.packetsPerMin * 0.06) },
        ]
      : [],
  };
}

export function SimulationProvider({ children }: { children: ReactNode }) {
  const [mode, setMode] = useState<SimulationMode>('default');
  const [progress, setProgress] = useState(0);
  const [base, setBase] = useState<DashboardData>(defaultDashboard);
  const [alerts, setAlerts] = useState<AlertItem[]>(defaultAlerts);
  const [lastUpdated, setLastUpdated] = useState(formatClock());
  const [series, setSeries] = useState<TrafficPoint[]>(() => buildTrafficSeries(24, 1.15));
  const [flows, setFlows] = useState<TrafficFlow[]>(() => buildTrafficFlows(16, 0.75));
  const raf = useRef<number | null>(null);
  const startTs = useRef(0);
  const alertInjected = useRef(false);
  const frozen = useRef<{ data: DashboardData; t: number } | null>(null);

  useEffect(() => {
    void getDashboardData().then(setBase);
    void getAlerts().then(setAlerts);
  }, []);

  const tick = useCallback((now: number) => {
    const t = clamp((now - startTs.current) / SIM_DURATION_MS, 0, 1);
    setProgress(t);
    setLastUpdated(formatClock());
    const scaled = scaleDashboard(resetDashboard, t);
    const trafficScale = lerp(0.85, 2.1, easeInOut(t));
    setSeries(buildTrafficSeries(24, trafficScale));
    setFlows(buildTrafficFlows(16, lerp(0.25, 1.05, t)));

    if (t >= 0.48 && !alertInjected.current) {
      alertInjected.current = true;
      const injected: AlertItem = {
        id: `sim-${Date.now()}`,
        timestamp: formatClock(),
        severity: 'CRITICAL',
        title: 'Possible DDoS attack predicted',
        threatType: 'DDoS',
        probability: 87,
        forecastWindow: 'Next 8 minutes',
        status: 'ACTIVE',
        recommendedAction: 'Enable SYN cookies, rate-limit edge UDP, and notify the on-call SOC analyst.',
        simulated: true,
      };
      setAlerts((prev) => [injected, ...prev.filter((a) => !a.simulated)]);
    }

    if (t >= 1) {
      setMode('stopped');
      frozen.current = { data: scaled, t: 1 };
      return;
    }
    raf.current = window.requestAnimationFrame(tick);
  }, []);

  const start = useCallback(() => {
    if (raf.current) window.cancelAnimationFrame(raf.current);
    alertInjected.current = false;
    frozen.current = null;
    setBase(resetDashboard);
    setAlerts(defaultAlerts.filter((a) => !a.simulated));
    setMode('running');
    setProgress(0);
    startTs.current = performance.now();
    raf.current = window.requestAnimationFrame(tick);
  }, [tick]);

  const stop = useCallback(() => {
    if (raf.current) window.cancelAnimationFrame(raf.current);
    raf.current = null;
    setMode('stopped');
    frozen.current = { data: scaleDashboard(resetDashboard, progress), t: progress };
  }, [progress]);

  const reset = useCallback(() => {
    if (raf.current) window.cancelAnimationFrame(raf.current);
    raf.current = null;
    alertInjected.current = false;
    frozen.current = null;
    setMode('reset');
    setProgress(0);
    setBase(resetDashboard);
    setAlerts(defaultAlerts.filter((a) => a.severity !== 'CRITICAL'));
    setSeries(buildTrafficSeries(24, 0.85));
    setFlows(buildTrafficFlows(16, 0.25));
    setLastUpdated(formatClock());
  }, []);

  useEffect(() => {
    return () => {
      if (raf.current) window.cancelAnimationFrame(raf.current);
    };
  }, []);

  const data = useMemo(() => {
    if (mode === 'running') return scaleDashboard(resetDashboard, progress);
    if (mode === 'stopped' && frozen.current) return frozen.current.data;
    if (mode === 'reset') return resetDashboard;
    return base;
  }, [mode, progress, base]);

  const snapshot = useMemo(() => {
    const t = mode === 'default' ? 0.72 : mode === 'reset' ? 0.04 : mode === 'stopped' ? (frozen.current?.t ?? progress) : progress;
    return snapshotFrom(data, t);
  }, [data, mode, progress]);

  const banner = useMemo(() => {
    if (mode === 'running' || mode === 'stopped') {
      if (data.attackProbability >= 61) {
        return `Potential DDoS attack predicted in approximately ${data.forecastHorizonMin} minutes.`;
      }
    }
    if (mode === 'default' && data.attackProbability >= 61) {
      return data.forecastMessage;
    }
    return null;
  }, [mode, data]);

  const value = useMemo<SimulationSnapshot>(
    () => ({
      mode,
      data,
      snapshot,
      series,
      flows,
      alerts,
      banner,
      lastUpdated,
      progress,
      start,
      stop,
      reset,
    }),
    [mode, data, snapshot, series, flows, alerts, banner, lastUpdated, progress, start, stop, reset],
  );

  return <SimulationContext.Provider value={value}>{children}</SimulationContext.Provider>;
}

export function useSimulation(): SimulationSnapshot {
  const ctx = useContext(SimulationContext);
  if (!ctx) throw new Error('useSimulation must be used within SimulationProvider');
  return ctx;
}
