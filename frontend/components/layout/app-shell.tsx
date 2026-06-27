'use client';

import { useEffect, type ReactNode } from 'react';

import { usePathname } from 'next/navigation';
import { Bell, ChevronDown, Menu, MoonStar, PanelLeft, Search, Shield, UserCircle2 } from 'lucide-react';

import { notificationSeed } from '@/constants/notifications';
import { futureWorkspaces, primaryWorkspaces } from '@/constants/workspaces';
import { NotificationCenter } from '@/components/feedback/notification-center';
import { SidebarItem } from '@/components/navigation/sidebar-item';
import { Breadcrumb } from '@/components/shared/breadcrumb';
import { NotificationBadge } from '@/components/feedback/notification-badge';
import { SearchBar } from '@/components/shared/search-bar';
import { Button } from '@/components/ui/button';
import { CommandPalette } from '@/components/workspace/command-palette';
import { GlobalSearchModal } from '@/components/workspace/global-search-modal';
import { cn } from '@/lib/utils';
import { useUIStore } from '@/store/ui-store';

function getActiveWorkspace(pathname: string) {
  if (pathname === '/') return 'Mission Control';
  const match = primaryWorkspaces.find((workspace) => pathname.startsWith(workspace.href) && workspace.href !== '/');
  return match?.label ?? 'Mission Control';
}

export function AppShell({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const {
    sidebarCollapsed,
    activeWorkspace: persistedWorkspace,
    theme,
    commandPaletteOpen,
    notificationCenterOpen,
    searchOpen,
    toggleSidebar,
    toggleTheme,
    setActiveWorkspace,
    setCommandPaletteOpen,
    setNotificationCenterOpen,
    setSearchOpen,
  } = useUIStore();
  const activeWorkspaceLabel = getActiveWorkspace(pathname ?? '/');
  const unreadCount = notificationSeed.filter((item) => !item.read).length;

  useEffect(() => {
    if (theme === 'system') {
      const media = window.matchMedia('(prefers-color-scheme: dark)');
      const applySystemTheme = () => {
        document.documentElement.setAttribute('data-theme', media.matches ? 'dark' : 'light');
      };

      applySystemTheme();
      media.addEventListener('change', applySystemTheme);
      return () => media.removeEventListener('change', applySystemTheme);
    }

    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  useEffect(() => {
    setActiveWorkspace(activeWorkspaceLabel);
  }, [activeWorkspaceLabel, setActiveWorkspace]);

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.ctrlKey && event.key.toLowerCase() === 'k') {
        event.preventDefault();
        setCommandPaletteOpen(true);
      }

      if (event.key === 'Escape') {
        setCommandPaletteOpen(false);
        setSearchOpen(false);
        setNotificationCenterOpen(false);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [setCommandPaletteOpen, setNotificationCenterOpen, setSearchOpen]);

  return (
    <div className="min-h-screen bg-background text-text-primary">
      <div className="flex min-h-screen">
        <aside
          className={cn(
            'fixed inset-y-0 left-0 z-20 hidden border-r border-border bg-sidebar text-white transition-all duration-200 xl:flex xl:flex-col',
            sidebarCollapsed ? 'w-20' : 'w-72',
          )}
        >
          <div className="flex h-16 items-center gap-3 border-b border-white/10 px-5">
            <div className="flex h-10 w-10 items-center justify-center rounded-panel bg-brand-primary text-white shadow-sm">
              <Shield className="h-5 w-5" aria-hidden="true" />
            </div>
            {!sidebarCollapsed ? (
              <div>
                <div className="text-sm font-semibold tracking-wide">LinkOps</div>
                <div className="text-xs text-white/60">Industrial Intelligence OS</div>
              </div>
            ) : null}
          </div>

          <div className="flex-1 overflow-y-auto px-3 py-4">
            <div className="space-y-1">
              {primaryWorkspaces.map((workspace) => (
                <SidebarItem
                  key={workspace.key}
                  href={workspace.href}
                  icon={workspace.icon}
                  label={workspace.label}
                  active={pathname === workspace.href}
                />
              ))}
            </div>

            <div className="mt-6 border-t border-white/10 pt-4">
              <div className="mb-3 px-3 text-[11px] uppercase tracking-[0.2em] text-white/50">Future</div>
              <div className="space-y-1">
                {futureWorkspaces.map((workspace) => (
                  <SidebarItem
                    key={workspace.key}
                    href={workspace.href}
                    icon={workspace.icon}
                    label={workspace.label}
                    comingSoon
                  />
                ))}
              </div>
            </div>
          </div>

          <div className="border-t border-white/10 p-4 text-xs text-white/55">
            LinkOps Mission Control
          </div>
        </aside>

        <div className={cn('flex min-h-screen flex-1 flex-col xl:pl-72', sidebarCollapsed && 'xl:pl-20')}>
          <header className="sticky top-0 z-30 border-b border-border bg-[color:var(--color-background)]/95 backdrop-blur-sm">
            <div className="flex h-16 items-center gap-3 px-4 md:px-6 lg:px-8">
              <Button variant="ghost" size="sm" className="xl:hidden" aria-label="Toggle sidebar" onClick={toggleSidebar}>
                <Menu className="h-4 w-4" />
              </Button>
              <Button variant="ghost" size="sm" className="hidden xl:inline-flex" aria-label="Collapse sidebar" onClick={toggleSidebar}>
                <PanelLeft className="h-4 w-4" />
              </Button>

              <div className="hidden md:block">
                <Breadcrumb items={[{ label: 'LinkOps' }, { label: activeWorkspaceLabel }]} />
              </div>

              <div className="ml-auto flex flex-1 items-center justify-end gap-3">
                <div className="hidden w-full max-w-xl lg:block">
                  <SearchBar onActivate={() => setSearchOpen(true)} />
                </div>
                <Button variant="ghost" size="sm" className="lg:hidden" aria-label="Open global search" onClick={() => setSearchOpen(true)}>
                  <Search className="h-4 w-4" />
                </Button>
                <Button variant="ghost" size="sm" aria-label="Open notifications" onClick={() => setNotificationCenterOpen(true)}>
                  <Bell className="h-4 w-4" />
                  <NotificationBadge count={unreadCount} />
                </Button>
                <Button variant="ghost" size="sm" onClick={toggleTheme} aria-label="Cycle theme mode: dark, light, system">
                  <MoonStar className="h-4 w-4" />
                </Button>
                <Button variant="secondary" size="sm" className="hidden md:inline-flex" aria-label="Workspace switcher">
                  <span>{persistedWorkspace}</span>
                  <ChevronDown className="h-4 w-4" />
                </Button>
                <Button variant="ghost" size="sm" aria-label="Profile menu">
                  <UserCircle2 className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </header>

          <main className="flex-1 px-4 py-6 md:px-6 lg:px-8 xl:px-10">
            <div className="mx-auto flex w-full max-w-[1600px] flex-col gap-6">{children}</div>
          </main>
        </div>
      </div>

      <CommandPalette open={commandPaletteOpen} onClose={() => setCommandPaletteOpen(false)} />
      <GlobalSearchModal open={searchOpen} onClose={() => setSearchOpen(false)} />
      <NotificationCenter open={notificationCenterOpen} notifications={notificationSeed} onClose={() => setNotificationCenterOpen(false)} />
    </div>
  );
}
