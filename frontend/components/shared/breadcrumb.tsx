export type BreadcrumbItem = {
  label: string;
  href?: string;
};

export function Breadcrumb({ items }: { items: BreadcrumbItem[] }) {
  return (
    <nav aria-label="Breadcrumb" className="flex items-center gap-2 text-sm text-text-secondary">
      {items.map((item, index) => (
        <div key={`${item.label}-${index}`} className="flex items-center gap-2">
          <span>{item.label}</span>
          {index < items.length - 1 ? <span className="text-border">/</span> : null}
        </div>
      ))}
    </nav>
  );
}
