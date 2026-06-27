import { PageHeader } from '@/components/shared/page-header';
import { EmptyState } from '@/components/feedback/empty-state';

export const metadata = {
  title: 'Live Monitoring',
};

export default function MonitorPage() {
  return (
    <>
      <PageHeader title="Live Monitoring" description="Future monitoring workspace reserved for operational signal views." actionLabel="View status" />
      <EmptyState title="Coming soon" description="Live monitoring will appear here as a dedicated future module." />
    </>
  );
}
