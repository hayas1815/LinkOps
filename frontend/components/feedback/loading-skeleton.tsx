export function LoadingSkeleton({ className }: { className?: string }) {
  return <div className={className ? `${className} animate-pulse rounded-card bg-panel` : 'animate-pulse rounded-card bg-panel'} />;
}
