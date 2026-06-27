import { LayoutDashboard, BookOpenText, Boxes, FileText, Sparkles, BarChart3, Settings, Radar, Wrench, ShieldCheck, Aperture } from 'lucide-react';

export type WorkspaceKey =
  | 'mission-control'
  | 'knowledge'
  | 'assets'
  | 'documents'
  | 'copilot'
  | 'analytics'
  | 'settings'
  | 'monitor'
  | 'maintenance'
  | 'compliance'
  | 'digital-twin';

export type WorkspaceDefinition = {
  key: WorkspaceKey;
  label: string;
  href: string;
  icon: typeof LayoutDashboard;
  comingSoon?: boolean;
};

export const primaryWorkspaces: WorkspaceDefinition[] = [
  { key: 'mission-control', label: 'Mission Control', href: '/', icon: LayoutDashboard },
  { key: 'knowledge', label: 'Knowledge Workspace', href: '/knowledge', icon: BookOpenText },
  { key: 'assets', label: 'Asset Workspace', href: '/assets', icon: Boxes },
  { key: 'documents', label: 'Document Workspace', href: '/documents', icon: FileText },
  { key: 'copilot', label: 'AI Workspace', href: '/copilot', icon: Sparkles },
  { key: 'analytics', label: 'Analytics Workspace', href: '/analytics', icon: BarChart3 },
  { key: 'settings', label: 'Settings', href: '/settings', icon: Settings },
];

export const futureWorkspaces: WorkspaceDefinition[] = [
  { key: 'monitor', label: 'Live Monitoring', href: '/monitor', icon: Radar, comingSoon: true },
  { key: 'digital-twin', label: 'Digital Twin', href: '/digital-twin', icon: Aperture, comingSoon: true },
  { key: 'compliance', label: 'Compliance Center', href: '/compliance', icon: ShieldCheck, comingSoon: true },
  { key: 'maintenance', label: 'Maintenance Intelligence', href: '/maintenance', icon: Wrench, comingSoon: true },
];

export const searchScopes = ['Assets', 'Documents', 'Knowledge', 'AI'] as const;
