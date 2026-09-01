import { SectionHeader } from '../components/common/SectionHeader';
import { SimulationControls } from '../components/simulation/SimulationControls';

export function Settings() {
  return (
    <div className="space-y-6">
      <SectionHeader
        eyebrow="Workspace"
        title="Settings"
        subtitle="Demo configuration only. API fields are placeholders for the FastAPI backend."
      />
      <SimulationControls />
      <section className="grid gap-4 xl:grid-cols-2">
        <article className="glass rounded-2xl p-5">
          <h2 className="text-sm font-semibold">Forecasting engine</h2>
          <label className="mt-4 block text-xs text-mute">
            Forecast horizon
            <select defaultValue="10 minutes" className="mt-2 w-full rounded-xl border border-white/10 bg-navy-2 px-3 py-2 text-sm text-ink">
              <option>5 minutes</option>
              <option>10 minutes</option>
              <option>15 minutes</option>
            </select>
          </label>
          <label className="mt-4 block text-xs text-mute">
            Refresh interval
            <select defaultValue="5 seconds" className="mt-2 w-full rounded-xl border border-white/10 bg-navy-2 px-3 py-2 text-sm text-ink">
              <option>2 seconds</option>
              <option>5 seconds</option>
              <option>15 seconds</option>
            </select>
          </label>
        </article>
        <article className="glass rounded-2xl p-5">
          <h2 className="text-sm font-semibold">Backend connection</h2>
          <p className="mt-2 text-xs text-mute">Not connected. The UI currently reads mock services in src/services/api.ts.</p>
          <label className="mt-4 block text-xs text-mute">
            FastAPI base URL
            <input
              className="mt-2 w-full rounded-xl border border-white/10 bg-navy-2 px-3 py-2 font-mono text-sm text-ink"
              defaultValue="http://127.0.0.1:8000"
              readOnly
            />
          </label>
          <ul className="mt-4 space-y-1 font-mono text-[11px] text-mute">
            <li>GET /dashboard</li>
            <li>GET /traffic</li>
            <li>GET /forecast</li>
            <li>GET /alerts</li>
            <li>GET /metrics</li>
            <li>POST /predict</li>
          </ul>
        </article>
      </section>
    </div>
  );
}
