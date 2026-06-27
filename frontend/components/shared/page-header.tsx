import { Button } from '@/components/ui/button';

export type PageHeaderProps = {
  title: string;
  description: string;
  actionLabel?: string;
};

export function PageHeader({ title, description, actionLabel }: PageHeaderProps) {
  return (
    <div className="flex flex-col gap-4 border-b border-border pb-6 md:flex-row md:items-end md:justify-between">
      <div className="max-w-3xl space-y-2">
        <h1 className="text-3xl font-semibold tracking-tight text-text-primary md:text-[2.5rem] md:leading-[3rem]">{title}</h1>
        <p className="text-sm leading-6 text-text-secondary md:text-base md:leading-6">{description}</p>
      </div>
      {actionLabel ? <Button size="md">{actionLabel}</Button> : null}
    </div>
  );
}
