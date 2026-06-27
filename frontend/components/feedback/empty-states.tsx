import { EmptyState } from '@/components/feedback/empty-state';

export function EmptyStateNoDocuments() {
  return (
    <EmptyState
      title="No Documents"
      description="No documents are available in this workspace yet. Upload files to begin indexing and processing."
      actionLabel="Upload document"
    />
  );
}

export function EmptyStateNoAssets() {
  return (
    <EmptyState
      title="No Assets"
      description="No assets have been registered yet. Create an asset to establish operational context."
      actionLabel="Add asset"
    />
  );
}

export function EmptyStateNoSearchResults() {
  return (
    <EmptyState
      title="No Search Results"
      description="No matching records were found. Refine your query or broaden the search scope."
    />
  );
}

export function EmptyStateOffline() {
  return (
    <EmptyState
      title="Offline"
      description="The workspace is currently offline. Reconnect to continue with synchronized platform operations."
      actionLabel="Retry connection"
    />
  );
}

export function EmptyStateNoNotifications() {
  return (
    <EmptyState
      title="No Notifications"
      description="You are up to date. Notification items will appear here when platform events are available."
    />
  );
}
