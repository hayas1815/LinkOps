import { PageHeader } from '@/components/shared/page-header';
import { Card, CardBody } from '@/components/ui/card';
import { SectionHeader } from '@/components/shared/section-header';
import { EmptyState } from '@/components/feedback/empty-state';

export const metadata = {
  title: 'AI Workspace',
};

export default function CopilotPage() {
  return (
    <>
      <PageHeader title="AI Workspace" description="Enterprise AI assistant placeholder for guided workflows and evidence-based support." actionLabel="New conversation" />
      <section className="grid gap-6 xl:grid-cols-[0.85fr_1.15fr_0.8fr]">
        <Card>
          <CardBody className="space-y-4">
            <SectionHeader title="Suggested Questions" description="Starter prompts for future guided interactions." />
            <div className="space-y-3 text-sm text-text-secondary">
              <div className="rounded-panel border border-border bg-panel px-4 py-3">What is the current status of pump maintenance?</div>
              <div className="rounded-panel border border-border bg-panel px-4 py-3">Which documents mention compliance updates?</div>
              <div className="rounded-panel border border-border bg-panel px-4 py-3">Summarize the latest asset alerts.</div>
            </div>
          </CardBody>
        </Card>
        <Card>
          <CardBody className="space-y-4">
            <SectionHeader title="Conversation Area" description="Future AI responses will appear here with traceable context." />
            <EmptyState title="No conversation yet" description="Ask a question to begin a future evidence-backed assistant session." actionLabel="Ask LinkOps" />
          </CardBody>
        </Card>
        <div className="space-y-4">
          <Card>
            <CardBody className="space-y-3">
              <SectionHeader title="Evidence Panel" description="Sources and references will appear here." />
              <div className="text-sm text-text-secondary">Sources placeholder</div>
            </CardBody>
          </Card>
          <Card>
            <CardBody className="space-y-3">
              <SectionHeader title="Confidence Score" description="Placeholder for future response confidence indicators." />
              <div className="text-2xl font-semibold text-text-primary">--</div>
            </CardBody>
          </Card>
        </div>
      </section>
    </>
  );
}
