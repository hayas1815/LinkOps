import type { Metadata } from 'next';
import type { ReactNode } from 'react';

import { AppProviders } from '@/app/providers';
import { AppShell } from '@/components/layout/app-shell';
import '@/styles/globals.css';

export const metadata: Metadata = {
  title: {
    default: 'LinkOps',
    template: '%s | LinkOps',
  },
  description: 'Industrial Knowledge Intelligence Platform',
  keywords: ['LinkOps', 'industrial intelligence', 'knowledge platform', 'enterprise SaaS'],
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en" data-theme="dark">
      <body>
        <AppProviders>
          <AppShell>{children}</AppShell>
        </AppProviders>
      </body>
    </html>
  );
}
