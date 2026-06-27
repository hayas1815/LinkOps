import { PageHeader } from '@/components/shared/page-header';
import { MetricCard } from '@/components/shared/metric-card';

export const metadata = {
    title: 'Analytics Workspace',
};

export default function AnalyticsPage() {
    return (
        <>
            <PageHeader title="Analytics Workspace" description="Cards-only analytics surface for platform health and coverage metrics." actionLabel="Export snapshot" />
            <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
                <MetricCard label="Knowledge Growth" value="24%" helper="Growth in indexed knowledge and references over the current period." trend="Up" tone="success" />
                <MetricCard label="Asset Coverage" value="428" helper="Operational assets represented in the platform data model." trend="Stable" tone="info" />
                <MetricCard label="Document Distribution" value="16.4K" helper="Documents distributed across processing and content groups." trend="+146" tone="default" />
                <MetricCard label="Compliance Readiness" value="81%" helper="Placeholder readiness indicator for future review workflows." trend="Review" tone="warning" />
                <MetricCard label="Processing Metrics" value="1.2K" helper="Operational documents and events processed by the platform." trend="Healthy" tone="success" />
            </section>
        </>
    );
}
