import { ArrowDown } from 'lucide-react';

const STAGES = [
  { title: 'Network Traffic', detail: 'Live flows, packets, protocols, flags' },
  { title: 'Data Ingestion', detail: 'Collectors normalize PCAP / NetFlow records' },
  { title: 'Preprocessing', detail: 'Cleaning, encoding, window alignment' },
  { title: 'Feature Extraction', detail: 'Rate, entropy, SYN ratio, duration' },
  { title: 'Isolation Forest', detail: 'Unsupervised anomaly detection layer' },
  { title: 'Anomaly Score', detail: '0–1 score fed into the sequence model' },
  { title: 'LSTM / GRU Model', detail: 'Temporal forecasting of attack likelihood' },
  { title: 'Attack Probability', detail: 'P(attack) over the forecast horizon' },
  { title: 'FastAPI Backend', detail: 'Future inference API — not connected yet' },
  { title: 'React Dashboard', detail: 'SOC visualization and analyst workflow' },
  { title: 'Security Alert', detail: 'Predictive alert with recommended action' },
];

export function ArchitectureFlow() {
  return (
    <ol className="mx-auto flex max-w-xl flex-col items-center">
      {STAGES.map((stage, i) => (
        <li key={stage.title} className="flex w-full flex-col items-center">
          <article className="glass w-full rounded-2xl px-5 py-4 text-center">
            <p className="font-mono text-[10px] uppercase tracking-[0.2em] text-cyan/70">Stage {i + 1}</p>
            <h3 className="mt-1 text-sm font-semibold">{stage.title}</h3>
            <p className="mt-1 text-xs text-mute">{stage.detail}</p>
          </article>
          {i < STAGES.length - 1 ? <ArrowDown className="my-2 h-4 w-4 text-cyan/50" /> : null}
        </li>
      ))}
    </ol>
  );
}
