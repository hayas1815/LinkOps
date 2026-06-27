import { PageHeader } from '@/components/shared/page-header';
import { UploadCard } from '@/components/feedback/upload-card';
import { Card, CardBody } from '@/components/ui/card';
import { SectionHeader } from '@/components/shared/section-header';
import { EmptyState } from '@/components/feedback/empty-state';

export const metadata = {
  title: 'Document Workspace',
};

export default function DocumentsPage() {
  return (
    <>
      <PageHeader title="Document Workspace" description="Professional upload and processing workspace for industrial documents." actionLabel="Upload document" />
      <section className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
        <UploadCard />
        <Card>
          <CardBody className="space-y-4">
            <SectionHeader title="Upload Queue" description="Queued documents and processing states appear here." />
            <EmptyState title="No files in queue" description="Upload documents to begin classification, extraction, and indexing." actionLabel="Browse files" />
          </CardBody>
        </Card>
      </section>
    </>
  );
}
