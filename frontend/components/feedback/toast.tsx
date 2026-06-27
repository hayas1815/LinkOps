import { CheckCircle2, AlertTriangle, XCircle, Info } from 'lucide-react';

import { cn } from '@/lib/utils';

export type ToastVariant = 'success' | 'warning' | 'error' | 'info';

export type ToastItem = {
  id: string;
  title: string;
  description?: string;
  variant: ToastVariant;
};

const iconMap = {
  success: CheckCircle2,
  warning: AlertTriangle,
  error: XCircle,
  info: Info,
} as const;

const toneMap: Record<ToastVariant, string> = {
  success: 'border-success/40 text-success',
  warning: 'border-warning/40 text-warning',
  error: 'border-danger/40 text-danger',
  info: 'border-info/40 text-info',
};

export function ToastMessage({ item }: { item: ToastItem }) {
  const Icon = iconMap[item.variant];

  return (
    <article className={cn('w-full rounded-panel border bg-card p-3 shadow-md', toneMap[item.variant])} role="status" aria-live="polite">
      <div className="flex items-start gap-3">
        <Icon className="mt-0.5 h-4 w-4" aria-hidden="true" />
        <div>
          <h4 className="text-sm font-semibold text-text-primary">{item.title}</h4>
          {item.description ? <p className="mt-1 text-sm text-text-secondary">{item.description}</p> : null}
        </div>
      </div>
    </article>
  );
}
