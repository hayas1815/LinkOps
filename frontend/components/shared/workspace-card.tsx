import { Card, CardBody, CardHeader } from '@/components/ui/card';

export type WorkspaceCardProps = {
  title: string;
  description: string;
  meta?: string;
};

export function WorkspaceCard({ title, description, meta }: WorkspaceCardProps) {
  return (
    <Card>
      <CardHeader>
        <div>
          <h3 className="text-sm font-semibold text-text-primary">{title}</h3>
          {meta ? <p className="mt-1 text-xs uppercase tracking-[0.18em] text-text-secondary">{meta}</p> : null}
        </div>
      </CardHeader>
      <CardBody>
        <p className="text-sm leading-6 text-text-secondary">{description}</p>
      </CardBody>
    </Card>
  );
}
