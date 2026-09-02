export function ModelMetricCard({
  label,
  value,
  hint,
}: {
  label: string;
  value: string;
  hint: string;
}) {
  return (
    <article className="glass rounded-2xl p-4">
      <p className="text-xs uppercase tracking-[0.14em] text-mute">{label}</p>
      <p className="mt-2 font-mono text-3xl font-semibold">{value}</p>
      <p className="mt-2 text-[11px] leading-relaxed text-mute">{hint}</p>
    </article>
  );
}
