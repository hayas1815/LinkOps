import { Command } from 'lucide-react';

import { Button } from '@/components/ui/button';
import { CommandPalettePlaceholder } from '@/components/workspace/command-palette-placeholder';

export function CommandPalette({ open, onClose }: { open: boolean; onClose: () => void }) {
  if (!open) {
    return null;
  }

  return (
    <div className="fixed inset-0 z-50 bg-black/50" onClick={onClose} aria-hidden="true">
      <section
        className="mx-auto mt-24 w-full max-w-2xl rounded-dialog border border-border bg-card p-4 shadow-lg"
        role="dialog"
        aria-label="Command Palette"
        onClick={(event) => event.stopPropagation()}
      >
        <div className="mb-3 flex items-center justify-between">
          <div className="flex items-center gap-2 text-sm font-semibold text-text-primary">
            <Command className="h-4 w-4 text-text-secondary" aria-hidden="true" />
            Command Palette
          </div>
          <Button size="sm" variant="ghost" onClick={onClose}>
            Esc
          </Button>
        </div>
        <label className="mb-3 block">
          <span className="sr-only">Search commands</span>
          <input
            type="text"
            placeholder="Type a command..."
            className="h-11 w-full rounded-input border border-border bg-panel px-4 text-sm text-text-primary outline-none focus-visible:shadow-focus"
            autoFocus
          />
        </label>
        <CommandPalettePlaceholder />
        <p className="mt-3 text-xs text-text-secondary">Keyboard shortcut: Ctrl + K. Placeholder only.</p>
      </section>
    </div>
  );
}
