'use client';

import type { ReactNode } from 'react';
import { QueryClientProvider } from '@tanstack/react-query';

import { ErrorBoundary } from '@/components/feedback/error-boundary';
import { ToastProvider } from '@/components/feedback/toast-provider';
import { queryClient } from '@/services/query-client';

export function AppProviders({ children }: { children: ReactNode }) {
  return (
    <QueryClientProvider client={queryClient}>
      <ToastProvider>
        <ErrorBoundary>{children}</ErrorBoundary>
      </ToastProvider>
    </QueryClientProvider>
  );
}
