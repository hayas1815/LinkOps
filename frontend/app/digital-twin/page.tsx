import { PageHeader } from '@/components/shared/page-header';
import { EmptyState } from '@/components/feedback/empty-state';

export const metadata = {
  title: 'Digital Twin',
};

export default function DigitalTwinPage() {
  return (
    <>
      <PageHeader title="Digital Twin" description="Future digital twin workspace for asset context and operational simulation readiness." actionLabel="View model" />
      <EmptyState title="Coming soon" description="Digital twin tools will appear here as a future module." />
    </>
  );
}
