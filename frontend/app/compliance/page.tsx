import { PageHeader } from '@/components/shared/page-header';
import { EmptyState } from '@/components/feedback/empty-state';

export const metadata = {
  title: 'Compliance Center',
};

export default function CompliancePage() {
  return (
    <>
      <PageHeader title="Compliance Center" description="Future module for compliance workflows, regulations, and readiness." actionLabel="View standards" />
      <EmptyState title="Coming soon" description="Compliance tools and readiness summaries will appear here." />
    </>
  );
}
