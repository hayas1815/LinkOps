import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export type ThemeMode = 'dark' | 'light' | 'system';

type UIState = {
  sidebarCollapsed: boolean;
  activeWorkspace: string;
  theme: ThemeMode;
  commandPaletteOpen: boolean;
  notificationCenterOpen: boolean;
  searchOpen: boolean;
  setSidebarCollapsed: (collapsed: boolean) => void;
  toggleSidebar: () => void;
  setActiveWorkspace: (workspace: string) => void;
  setTheme: (theme: ThemeMode) => void;
  toggleTheme: () => void;
  setCommandPaletteOpen: (open: boolean) => void;
  setNotificationCenterOpen: (open: boolean) => void;
  setSearchOpen: (open: boolean) => void;
};

export const useUIStore = create<UIState>()(
  persist(
    (set) => ({
      sidebarCollapsed: false,
      activeWorkspace: 'Mission Control',
      theme: 'system',
      commandPaletteOpen: false,
      notificationCenterOpen: false,
      searchOpen: false,
      setSidebarCollapsed: (collapsed) => set({ sidebarCollapsed: collapsed }),
      toggleSidebar: () => set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),
      setActiveWorkspace: (workspace) => set({ activeWorkspace: workspace }),
      setTheme: (theme) => set({ theme }),
      toggleTheme: () =>
        set((state) => ({
          theme:
            state.theme === 'dark'
              ? 'light'
              : state.theme === 'light'
                ? 'system'
                : 'dark',
        })),
      setCommandPaletteOpen: (open) => set({ commandPaletteOpen: open }),
      setNotificationCenterOpen: (open) => set({ notificationCenterOpen: open }),
      setSearchOpen: (open) => set({ searchOpen: open }),
    }),
    {
      name: 'linkops-ui-state',
      partialize: (state) => ({
        sidebarCollapsed: state.sidebarCollapsed,
        activeWorkspace: state.activeWorkspace,
        theme: state.theme,
      }),
    },
  ),
);
