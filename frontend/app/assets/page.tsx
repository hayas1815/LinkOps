import { PageHeader } from '@/components/shared/page-header';
import { Card, CardBody } from '@/components/ui/card';
import { SectionHeader } from '@/components/shared/section-header';
import { WorkspaceCard } from '@/components/shared/workspace-card';

export const metadata = {
  title: 'Asset Workspace',
};

export default function AssetsPage() {
  return (
    <>
      <PageHeader title="Asset Workspace" description="Enterprise asset explorer for operational context and future intelligence." actionLabel="Add asset" />
      <section className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
        <Card>
          <CardBody className="space-y-4">
            <SectionHeader title="Asset Cards" description="Search, filter, and review assets from a production-ready layout." />
            <div className="grid gap-4 md:grid-cols-2">
              <WorkspaceCard title="Pump A-102" description="Critical process asset with maintenance, document, and knowledge context." meta="Active" />
              <WorkspaceCard title="Motor M-204" description="Rotating equipment placeholder for operational details and future sensors." meta="Monitored" />
            </div>
          </CardBody>
        </Card>
        <Card>
          <CardBody className="space-y-4">
            <SectionHeader title="Asset Detail Placeholder" description="Tabs for overview, documents, maintenance, knowledge, history, and future sensors." />
            <div className="grid gap-3 text-sm text-text-secondary">
              <div className="rounded-panel border border-border bg-panel px-4 py-3">Overview</div>
              <div className="rounded-panel border border-border bg-panel px-4 py-3">Documents</div>
              <div className="rounded-panel border border-border bg-panel px-4 py-3">Maintenance</div>
              <div className="rounded-panel border border-border bg-panel px-4 py-3">Knowledge</div>
              <div className="rounded-panel border border-border bg-panel px-4 py-3">History</div>
              <div className="rounded-panel border border-border bg-panel px-4 py-3">Future Sensors</div>
            </div>
          </CardBody>
        </Card>
      </section>
    </>
  );
}
