import type { ReactNode } from 'react';

import { cn } from '@/lib/utils';

export function Panel({ className, children }: { className?: string; children: ReactNode }) {
  return <section className={cn('rounded-panel border border-border bg-card p-5 shadow-sm', className)}>{children}</section>;
}
