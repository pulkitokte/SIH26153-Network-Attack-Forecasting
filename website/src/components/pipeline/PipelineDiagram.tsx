import { ArrowRight } from 'lucide-react';
import type { PipelineStage } from '../../types';

export function PipelineDiagram({ stages }: { stages: PipelineStage[] }) {
  return (
    <div className="flex flex-wrap items-stretch gap-2">
      {stages.map((stage, i) => (
        <div key={stage.id} className="flex min-w-[140px] flex-1 items-stretch gap-2">
          <article className="glass flex-1 rounded-2xl p-4">
            <p className="font-mono text-[10px] uppercase tracking-[0.16em] text-cyan/80">{String(i + 1).padStart(2, '0')}</p>
            <h3 className="mt-2 text-sm font-semibold">{stage.title}</h3>
            <p className="mt-2 text-xs leading-relaxed text-mute">{stage.description}</p>
          </article>
          {i < stages.length - 1 ? (
            <div className="hidden items-center text-cyan/50 lg:flex">
              <ArrowRight className="h-4 w-4" />
            </div>
          ) : null}
        </div>
      ))}
    </div>
  );
}
