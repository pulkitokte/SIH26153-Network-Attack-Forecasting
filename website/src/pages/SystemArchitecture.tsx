import { ArchitectureFlow } from '../components/architecture/ArchitectureFlow';
import { PipelineDiagram } from '../components/pipeline/PipelineDiagram';
import { SectionHeader } from '../components/common/SectionHeader';
import { pipelineStages } from '../data/mock';

export function SystemArchitecture() {
  return (
    <div className="space-y-6">
      <SectionHeader
        eyebrow="System design"
        title="System Architecture"
        subtitle="End-to-end path from raw traffic to a predictive SOC alert. FastAPI is shown as the future inference layer."
      />
      <section className="glass rounded-2xl p-6">
        <h2 className="mb-6 text-center text-sm font-semibold uppercase tracking-[0.18em] text-mute">Inference path</h2>
        <ArchitectureFlow />
      </section>
      <section>
        <h2 className="mb-3 text-lg font-semibold">Pipeline detail</h2>
        <PipelineDiagram stages={pipelineStages} />
      </section>
    </div>
  );
}
