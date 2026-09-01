import { Play, RotateCcw, Square } from 'lucide-react';
import { useSimulation } from '../../context/SimulationContext';
import { cn } from '../../utils/format';

export function SimulationControls({ compact = false }: { compact?: boolean }) {
  const { mode, start, stop, reset, progress } = useSimulation();
  const running = mode === 'running';

  if (compact) {
    return (
      <div className="flex items-center gap-1.5">
        <button
          type="button"
          onClick={running ? stop : start}
          className={cn(
            'rounded-lg border px-2.5 py-1.5 font-mono text-[11px] uppercase tracking-wide transition',
            running
              ? 'border-critical/40 bg-critical/10 text-critical hover:bg-critical/15'
              : 'border-cyan/30 bg-cyan/10 text-cyan hover:bg-cyan/15',
          )}
        >
          {running ? 'Stop' : 'Simulate'}
        </button>
        <button
          type="button"
          onClick={reset}
          className="rounded-lg border border-white/10 px-2 py-1.5 text-mute hover:text-ink"
          aria-label="Reset simulation"
        >
          <RotateCcw className="h-3.5 w-3.5" />
        </button>
      </div>
    );
  }

  return (
    <div className="glass rounded-2xl p-4">
      <div className="mb-3 flex items-center justify-between">
        <div>
          <p className="font-mono text-[11px] uppercase tracking-[0.16em] text-cyan/80">Demo mode</p>
          <h3 className="mt-1 text-sm font-semibold">Attack simulation</h3>
        </div>
        <span className="font-mono text-[11px] text-mute">{Math.round(progress * 100)}%</span>
      </div>
      <div className="mb-4 h-1 overflow-hidden rounded-full bg-white/8">
        <div className="h-full bg-cyan transition-all" style={{ width: `${Math.round(progress * 100)}%` }} />
      </div>
      <div className="flex flex-wrap gap-2">
        <button
          type="button"
          onClick={start}
          disabled={running}
          className="inline-flex items-center gap-2 rounded-lg bg-cyan px-3 py-2 text-sm font-medium text-navy hover:bg-cyan-2 disabled:opacity-50"
        >
          <Play className="h-4 w-4" />
          Start Attack Simulation
        </button>
        <button
          type="button"
          onClick={stop}
          className="inline-flex items-center gap-2 rounded-lg border border-white/10 px-3 py-2 text-sm text-ink hover:bg-white/5"
        >
          <Square className="h-4 w-4" />
          Stop Simulation
        </button>
        <button
          type="button"
          onClick={reset}
          className="inline-flex items-center gap-2 rounded-lg border border-white/10 px-3 py-2 text-sm text-ink hover:bg-white/5"
        >
          <RotateCcw className="h-4 w-4" />
          Reset Simulation
        </button>
      </div>
      <p className="mt-3 text-xs text-mute">
        Frontend-only demo. Traffic, anomaly score, and attack probability rise from SAFE → CRITICAL.
      </p>
    </div>
  );
}
