export function SectionHeader({ title, description }: { title: string; description?: string }) {
  return (
    <div className="space-y-1">
      <h2 className="text-base font-semibold text-text-primary">{title}</h2>
      {description ? <p className="text-sm leading-6 text-text-secondary">{description}</p> : null}
    </div>
  );
}
