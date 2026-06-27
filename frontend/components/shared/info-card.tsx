import { Card, CardBody, CardHeader } from '@/components/ui/card';

export type InfoCardProps = {
  title: string;
  description: string;
  footer?: string;
};

export function InfoCard({ title, description, footer }: InfoCardProps) {
  return (
    <Card>
      <CardHeader>
        <h3 className="text-sm font-semibold text-text-primary">{title}</h3>
      </CardHeader>
      <CardBody>
        <p className="text-sm leading-6 text-text-secondary">{description}</p>
        {footer ? <p className="mt-4 text-xs uppercase tracking-[0.16em] text-text-secondary">{footer}</p> : null}
      </CardBody>
    </Card>
  );
}
