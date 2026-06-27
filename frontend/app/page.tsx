import { Sparkles, Activity, AlertTriangle, ArrowRight, FileText, Layers3, Plus, ShieldCheck, Workflow } from 'lucide-react';

import { MetricCard } from '@/components/shared/metric-card';
import { InfoCard } from '@/components/shared/info-card';
import { WorkspaceCard } from '@/components/shared/workspace-card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { PageHeader } from '@/components/shared/page-header';
import { SectionHeader } from '@/components/shared/section-header';
import { Card, CardBody } from '@/components/ui/card';

const quickActions = [
  'Upload document',
  'Review queue',
  'Open asset',
  'Check alerts',
];

const recentItems = [
  { title: 'Pump inspection report', detail: 'Uploaded 12 min ago' },
  { title: 'Maintenance note synced', detail: 'Updated 27 min ago' },
  { title: 'Compliance packet indexed', detail: 'Processed 41 min ago' },
];

export default function MissionControlPage() {
  return (
    <>
      <PageHeader
        title="Mission Control"
        description="Operational visibility across knowledge, assets, documents, and intelligence workflows."
        actionLabel="Open workspace"
      />

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <MetricCard label="System Health" value="99.8%" helper="Platform services stable across the last 24 hours." trend="Stable" tone="success" />
        <MetricCard label="Knowledge Nodes" value="1,284" helper="Structured relationships ready for future graph expansion." trend="+12%" tone="info" />
        <MetricCard label="Connected Assets" value="428" helper="Assets currently tracked within the operational model." trend="+8" tone="default" />
        <MetricCard label="Documents" value="16.4K" helper="Indexed documents and technical records." trend="+146" tone="info" />
      </section>

      <section className="grid gap-6 xl:grid-cols-[1.6fr_1fr]">
        <Card>
          <CardBody className="space-y-6">
            <SectionHeader title="Quick Actions" description="Common operational shortcuts for daily work." />
            <div className="flex flex-wrap gap-3">
              {quickActions.map((action) => (
                <Button key={action} variant="secondary" size="md">
                  {action}
                </Button>
              ))}
            </div>
            <div className="grid gap-4 md:grid-cols-2">
              <WorkspaceCard title="Platform Status" description="Backend services, document processing, and search infrastructure are currently healthy." meta="Mission ready" />
              <WorkspaceCard title="AI Insights" description="Placeholder for future insight summaries and AI-supported operational context." meta="AI workspace" />
            </div>
          </CardBody>
        </Card>

        <div className="space-y-4">
          <InfoCard title="Processing Queue" description="Documents and future work items will appear here with transparent operational status." footer="Queue visibility" />
          <InfoCard title="Recent Alerts" description="Operational alerts will surface with severity, context, and resolution status." footer="Alert monitoring" />
        </div>
      </section>

      <section className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardBody className="space-y-4">
            <SectionHeader title="Recent Uploads" description="Latest documents moving through the platform." />
            <div className="space-y-3">
              {recentItems.map((item) => (
                <div key={item.title} className="flex items-center justify-between rounded-panel border border-border bg-panel px-4 py-3">
                  <div>
                    <p className="text-sm font-medium text-text-primary">{item.title}</p>
                    <p className="text-xs text-text-secondary">{item.detail}</p>
                  </div>
                  <Badge tone="neutral">Processing</Badge>
                </div>
              ))}
            </div>
          </CardBody>
        </Card>

        <Card>
          <CardBody className="space-y-4">
            <SectionHeader title="Recent Activity" description="Operational history and user actions in the platform." />
            <div className="space-y-3">
              {[
                'Knowledge workspace opened',
                'Document parsing completed',
                'Asset reference created',
              ].map((event) => (
                <div key={event} className="flex items-center justify-between rounded-panel border border-border bg-panel px-4 py-3">
                  <span className="text-sm text-text-primary">{event}</span>
                  <ArrowRight className="h-4 w-4 text-text-secondary" aria-hidden="true" />
                </div>
              ))}
            </div>
          </CardBody>
        </Card>
      </section>

      <section className="grid gap-6 xl:grid-cols-3">
        <InfoCard title="Recent Maintenance" description="Maintenance intelligence will surface service history, work notes, and next actions." footer="Maintenance readiness" />
        <InfoCard title="Documents" description="Document counts, processing status, and readiness indicators are tracked here." footer="Content intelligence" />
        <InfoCard title="Quick Actions" description="Direct shortcuts for upload, review, and exploratory workflows." footer="Operator efficiency" />
      </section>
    </>
  );
}
