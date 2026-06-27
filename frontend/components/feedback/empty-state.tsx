import { Button } from '@/components/ui/button';

export function EmptyState({ title, description, actionLabel }: { title: string; description: string; actionLabel?: string }) {
  return (
    <div className="rounded-card border border-border bg-card p-6 text-center shadow-sm">
      <h3 className="text-base font-semibold text-text-primary">{title}</h3>
      <p className="mt-2 text-sm leading-6 text-text-secondary">{description}</p>
      {actionLabel ? <Button className="mt-4">{actionLabel}</Button> : null}
    </div>
  );
}
