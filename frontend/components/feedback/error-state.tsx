import { Button } from '@/components/ui/button';

export function ErrorState({
  title,
  description,
  actionLabel = 'Retry',
  onAction,
}: {
  title: string;
  description: string;
  actionLabel?: string;
  onAction?: () => void;
}) {
  return (
    <div className="rounded-card border border-border bg-card p-6 shadow-sm">
      <h3 className="text-base font-semibold text-text-primary">{title}</h3>
      <p className="mt-2 text-sm leading-6 text-text-secondary">{description}</p>
      <Button className="mt-4" variant="secondary" onClick={onAction}>
        {actionLabel}
      </Button>
    </div>
  );
}
