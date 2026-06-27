import { Search } from 'lucide-react';

import { searchScopes } from '@/constants/workspaces';
import { EmptyStateNoSearchResults } from '@/components/feedback/empty-states';
import { Button } from '@/components/ui/button';

export function GlobalSearchModal({ open, onClose }: { open: boolean; onClose: () => void }) {
  if (!open) {
    return null;
  }

  return (
    <div className="fixed inset-0 z-50 bg-black/50" onClick={onClose} aria-hidden="true">
      <section
        className="mx-auto mt-20 w-full max-w-3xl rounded-dialog border border-border bg-card p-5 shadow-lg"
        role="dialog"
        aria-label="Global Search"
        onClick={(event) => event.stopPropagation()}
      >
        <div className="mb-4 flex items-center justify-between">
          <h2 className="flex items-center gap-2 text-sm font-semibold text-text-primary">
            <Search className="h-4 w-4 text-text-secondary" aria-hidden="true" />
            Global Search
          </h2>
          <Button variant="ghost" size="sm" onClick={onClose}>
            Close
          </Button>
        </div>

        <label className="mb-4 block">
          <span className="sr-only">Search query</span>
          <input
            type="search"
            placeholder="Search across assets, documents, knowledge, and AI"
            className="h-11 w-full rounded-input border border-border bg-panel px-4 text-sm text-text-primary outline-none focus-visible:shadow-focus"
            autoFocus
          />
        </label>

        <div className="mb-4 flex flex-wrap gap-2">
          {searchScopes.map((scope) => (
            <span key={scope} className="rounded-full border border-border bg-panel px-3 py-1 text-xs uppercase tracking-[0.14em] text-text-secondary">
              {scope}
            </span>
          ))}
        </div>

        <EmptyStateNoSearchResults />
        <p className="mt-4 text-xs text-text-secondary">Future integration placeholder: global search will aggregate assets, documents, knowledge, and AI context.</p>
      </section>
    </div>
  );
}
