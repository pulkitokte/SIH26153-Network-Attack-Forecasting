import type { RiskLevel } from '../types';

export function getRiskLevel(probability: number): RiskLevel {
  if (probability <= 30) return 'SAFE';
  if (probability <= 60) return 'WATCH';
  if (probability <= 80) return 'HIGH';
  return 'CRITICAL';
}

export function getRiskCopy(level: RiskLevel): string {
  switch (level) {
    case 'SAFE':
      return 'Network conditions are within baseline. No attack forecasted.';
    case 'WATCH':
      return 'Traffic patterns are drifting. Continue monitoring the forecast window.';
    case 'HIGH':
      return 'Elevated probability of an attack in the near term.';
    case 'CRITICAL':
      return 'High-confidence attack forecast. Prepare containment actions.';
  }
}

export function getAnomalyLabel(score: number): 'Normal' | 'Suspicious' | 'Anomalous' | 'Critical' {
  if (score < 0.3) return 'Normal';
  if (score < 0.55) return 'Suspicious';
  if (score < 0.8) return 'Anomalous';
  return 'Critical';
}

export function clamp(value: number, min = 0, max = 100): number {
  return Math.min(max, Math.max(min, value));
}

export function lerp(from: number, to: number, t: number): number {
  return from + (to - from) * t;
}

export function easeInOut(t: number): number {
  return t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2;
}
