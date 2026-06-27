import { Search } from 'lucide-react';

export function SearchBar({ onActivate }: { onActivate?: () => void }) {
  return (
    <button
      type="button"
      onClick={onActivate}
      className="flex h-11 w-full items-center gap-3 rounded-input border border-border bg-panel px-4 text-left text-sm text-text-secondary shadow-sm transition-colors duration-200 hover:bg-card focus-visible:outline-none focus-visible:shadow-focus"
      aria-label="Open global search"
    >
      <Search className="h-4 w-4 shrink-0" aria-hidden="true" />
      <span className="text-text-secondary">Search assets, documents, knowledge, AI</span>
      <span className="ml-auto rounded border border-border px-2 py-0.5 text-[11px] uppercase tracking-[0.14em] text-text-secondary">Ctrl + K</span>
    </button>
  );
}
