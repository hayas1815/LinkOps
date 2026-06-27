import { Bell } from 'lucide-react';

import type { AppNotification } from '@/constants/notifications';
import { EmptyStateNoNotifications } from '@/components/feedback/empty-states';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';

const toneMap: Record<AppNotification['severity'], 'info' | 'success' | 'warning' | 'danger'> = {
  info: 'info',
  success: 'success',
  warning: 'warning',
  error: 'danger',
};

export function NotificationCenter({
  open,
  notifications,
  onClose,
}: {
  open: boolean;
  notifications: AppNotification[];
  onClose: () => void;
}) {
  if (!open) {
    return null;
  }

  return (
    <div className="fixed inset-0 z-40 bg-black/40" onClick={onClose} aria-hidden="true">
      <section
        className="absolute right-4 top-20 w-[24rem] rounded-dialog border border-border bg-card p-4 shadow-lg"
        role="dialog"
        aria-label="Notification Center"
        onClick={(event) => event.stopPropagation()}
      >
        <div className="mb-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Bell className="h-4 w-4 text-text-secondary" aria-hidden="true" />
            <h2 className="text-sm font-semibold text-text-primary">Notification Center</h2>
          </div>
          <Button variant="ghost" size="sm" onClick={onClose}>
            Close
          </Button>
        </div>

        {notifications.length === 0 ? (
          <EmptyStateNoNotifications />
        ) : (
          <div className="max-h-[24rem] space-y-3 overflow-y-auto">
            {notifications.map((notification) => (
              <article key={notification.id} className="rounded-panel border border-border bg-panel p-3">
                <div className="mb-2 flex items-center justify-between gap-3">
                  <h3 className="text-sm font-medium text-text-primary">{notification.title}</h3>
                  <Badge tone={toneMap[notification.severity]}>{notification.severity}</Badge>
                </div>
                <p className="text-sm text-text-secondary">{notification.description}</p>
                <p className="mt-2 text-xs uppercase tracking-[0.16em] text-text-secondary">{notification.timestamp}</p>
              </article>
            ))}
          </div>
        )}

        <p className="mt-4 text-xs text-text-secondary">Future integration placeholder: notifications will connect to platform events and workflow updates.</p>
      </section>
    </div>
  );
}
