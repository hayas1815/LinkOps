export type WorkspaceStatus = 'active' | 'idle' | 'warning' | 'critical' | 'offline' | 'coming-soon';

export type MetricItem = {
  label: string;
  value: string;
  trend?: string;
  status?: WorkspaceStatus;
  helper?: string;
};
