import { PageHeader } from '@/components/shared/page-header';
import { Card, CardBody } from '@/components/ui/card';
import { SectionHeader } from '@/components/shared/section-header';

export const metadata = {
  title: 'Knowledge Workspace',
};

export default function KnowledgePage() {
  return (
    <>
      <PageHeader title="Knowledge Workspace" description="Knowledge graph placeholder with a large canvas and relationship context." actionLabel="Open graph" />
      <section className="grid gap-6 xl:grid-cols-[1.4fr_0.6fr]">
        <Card>
          <CardBody className="min-h-[42rem] space-y-4">
            <SectionHeader title="Visualization Canvas" description="Future interactive graph area for entities, relationships, and exploration." />
            <div className="flex min-h-[34rem] items-center justify-center rounded-panel border border-dashed border-border bg-panel text-sm text-text-secondary">
              Future interactive graph canvas
            </div>
          </CardBody>
        </Card>
        <div className="space-y-4">
          <Card>
            <CardBody className="space-y-3">
              <SectionHeader title="Legend" description="Placeholder for node and relationship types." />
              <div className="text-sm text-text-secondary">Assets, documents, regulations, incidents, and operators will be represented here.</div>
            </CardBody>
          </Card>
          <Card>
            <CardBody className="space-y-3">
              <SectionHeader title="Relationship Panel" description="Future contextual details for selected graph elements." />
              <div className="text-sm text-text-secondary">Select an entity to inspect incoming and outgoing relationships.</div>
            </CardBody>
          </Card>
        </div>
      </section>
    </>
  );
}
