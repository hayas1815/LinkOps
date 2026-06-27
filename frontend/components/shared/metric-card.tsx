import { Card, CardBody, CardHeader } from '@/components/ui/card';
import { Badge, type BadgeTone } from '@/components/ui/badge';

export type MetricCardProps = {
  label: string;
  value: string;
  helper?: string;
  trend?: string;
  tone?: BadgeTone;
};

export function MetricCard({ label, value, helper, trend, tone = 'default' }: MetricCardProps) {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-start justify-between gap-4">
          <div>
            <p className="text-xs uppercase tracking-[0.18em] text-text-secondary">{label}</p>
            <p className="mt-2 text-2xl font-semibold text-text-primary">{value}</p>
          </div>
          {trend ? <Badge tone={tone}>{trend}</Badge> : null}
        </div>
      </CardHeader>
      {helper ? <CardBody><p className="text-sm text-text-secondary">{helper}</p></CardBody> : null}
    </Card>
  );
}
