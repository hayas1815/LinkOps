export type AppNotification = {
  id: string;
  title: string;
  description: string;
  severity: 'info' | 'success' | 'warning' | 'error';
  read: boolean;
  timestamp: string;
};

export const notificationSeed: AppNotification[] = [
  {
    id: 'notif-1',
    title: 'Document ingestion completed',
    description: 'Batch processing finished for uploaded maintenance records.',
    severity: 'success',
    read: false,
    timestamp: '2m ago',
  },
  {
    id: 'notif-2',
    title: 'Knowledge index refresh pending',
    description: 'Scheduled refresh queued for the next orchestration window.',
    severity: 'warning',
    read: false,
    timestamp: '8m ago',
  },
  {
    id: 'notif-3',
    title: 'Platform snapshot archived',
    description: 'Operational snapshot is available in analytics exports.',
    severity: 'info',
    read: true,
    timestamp: '31m ago',
  },
];
