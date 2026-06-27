import type { ReactNode } from 'react';

export function Modal({ children }: { children: ReactNode }) {
  return <div className="rounded-dialog border border-border bg-card shadow-lg">{children}</div>;
}
