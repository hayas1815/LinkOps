import { PageHeader } from '@/components/shared/page-header';
import { EmptyState } from '@/components/feedback/empty-state';

export const metadata = {
  title: 'Maintenance Intelligence',
};

export default function MaintenancePage() {
  return (
    <>
      <PageHeader title="Maintenance Intelligence" description="Future module for maintenance workflows, records, and planning context." actionLabel="Open records" />
      <EmptyState title="Coming soon" description="Maintenance intelligence will appear here as a future workspace module." />
    </>
  );
}
