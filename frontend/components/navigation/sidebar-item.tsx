import Link from 'next/link';
import { type LucideIcon } from 'lucide-react';

import { cn } from '@/lib/utils';

export type SidebarItemProps = {
  href: string;
  icon: LucideIcon;
  label: string;
  active?: boolean;
  comingSoon?: boolean;
};

export function SidebarItem({ href, icon: Icon, label, active, comingSoon }: SidebarItemProps) {
  return (
    <Link
      href={href}
      className={cn(
        'flex items-center justify-between rounded-button px-3 py-2 text-sm font-medium transition-colors duration-200',
        active
          ? 'bg-brand-primary text-white shadow-sm'
          : 'text-text-secondary hover:bg-panel hover:text-text-primary',
      )}
    >
      <span className="flex items-center gap-3">
        <Icon className="h-4 w-4 shrink-0" aria-hidden="true" />
        <span>{label}</span>
      </span>
      {comingSoon ? <span className="text-[11px] uppercase tracking-[0.18em] text-text-secondary">Coming soon</span> : null}
    </Link>
  );
}
