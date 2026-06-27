import type { ReactNode } from 'react';

export function Drawer({ children }: { children: ReactNode }) {
  return <aside className="rounded-panel border border-border bg-card shadow-md">{children}</aside>;
}
