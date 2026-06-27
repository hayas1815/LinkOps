import Link from 'next/link';

import { EmptyState } from '@/components/feedback/empty-state';

export default function NotFound() {
  return (
    <div className="grid min-h-[60vh] place-items-center">
      <div className="w-full max-w-xl">
        <EmptyState title="Page not found" description="The requested workspace or page does not exist." actionLabel="Back to Mission Control" />
        <div className="mt-4 text-center text-sm text-text-secondary">
          <Link href="/">Return to home</Link>
        </div>
      </div>
    </div>
  );
}
