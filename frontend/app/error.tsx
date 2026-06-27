'use client';

import { useEffect } from 'react';

import { ErrorState } from '@/components/feedback/error-state';

export default function Error({ error, reset }: { error: Error & { digest?: string }; reset: () => void }) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <ErrorState
      title="Something went wrong"
      description="The workspace failed to render. Try again to reload the current view."
      actionLabel="Try again"
      onAction={reset}
    />
  );
}
