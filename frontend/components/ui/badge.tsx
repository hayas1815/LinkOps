import * as React from 'react';

import { cn } from '@/lib/utils';

export type BadgeTone = 'default' | 'success' | 'warning' | 'danger' | 'info' | 'neutral';

const toneClasses: Record<BadgeTone, string> = {
  default: 'bg-brand-primary/15 text-brand-primary border-brand-primary/30',
  success: 'bg-success/15 text-success border-success/30',
  warning: 'bg-warning/15 text-warning border-warning/30',
  danger: 'bg-danger/15 text-danger border-danger/30',
  info: 'bg-info/15 text-info border-info/30',
  neutral: 'bg-neutral/15 text-text-secondary border-border',
};

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  tone?: BadgeTone;
}

export function Badge({ className, tone = 'default', ...props }: BadgeProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full border px-2.5 py-1 text-xs font-medium uppercase tracking-wide',
        toneClasses[tone],
        className,
      )}
      {...props}
    />
  );
}
