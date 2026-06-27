import { LoadingSkeleton } from '@/components/feedback/loading-skeleton';

export default function Loading() {
  return (
    <div className="space-y-6" aria-label="Loading page">
      <LoadingSkeleton className="h-20 w-full" />
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <LoadingSkeleton className="h-28" />
        <LoadingSkeleton className="h-28" />
        <LoadingSkeleton className="h-28" />
        <LoadingSkeleton className="h-28" />
      </div>
      <LoadingSkeleton className="h-96 w-full" />
    </div>
  );
}
