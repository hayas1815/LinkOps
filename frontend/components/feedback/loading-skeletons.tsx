import { LoadingSkeleton } from '@/components/feedback/loading-skeleton';

export function CardSkeleton() {
  return <LoadingSkeleton className="h-28 w-full" />;
}

export function PageSkeleton() {
  return (
    <div className="space-y-4">
      <LoadingSkeleton className="h-20 w-full" />
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <CardSkeleton />
        <CardSkeleton />
        <CardSkeleton />
        <CardSkeleton />
      </div>
      <LoadingSkeleton className="h-80 w-full" />
    </div>
  );
}

export function SidebarSkeleton() {
  return (
    <div className="space-y-2">
      <LoadingSkeleton className="h-10 w-full" />
      <LoadingSkeleton className="h-10 w-full" />
      <LoadingSkeleton className="h-10 w-full" />
      <LoadingSkeleton className="h-10 w-full" />
    </div>
  );
}
