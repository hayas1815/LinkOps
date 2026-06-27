import { PageHeader } from '@/components/shared/page-header';
import { Card, CardBody } from '@/components/ui/card';
import { SectionHeader } from '@/components/shared/section-header';

export const metadata = {
  title: 'Settings',
};

export default function SettingsPage() {
  return (
    <>
      <PageHeader title="Settings" description="Organization, users, permissions, integrations, appearance, and system preferences." actionLabel="Save changes" />
      <section className="grid gap-6 lg:grid-cols-2">
        <Card><CardBody><SectionHeader title="Organization" description="Company profile, identity, and operational metadata." /></CardBody></Card>
        <Card><CardBody><SectionHeader title="Users" description="User administration placeholder for future enterprise access management." /></CardBody></Card>
        <Card><CardBody><SectionHeader title="Permissions" description="Role and access structure placeholder for future use." /></CardBody></Card>
        <Card><CardBody><SectionHeader title="Integrations" description="Connected systems, data inputs, and external services." /></CardBody></Card>
        <Card><CardBody><SectionHeader title="Appearance" description="Theme, density, and workspace preferences." /></CardBody></Card>
        <Card><CardBody><SectionHeader title="System" description="Runtime and environment settings." /></CardBody></Card>
        <Card className="lg:col-span-2"><CardBody><SectionHeader title="About LinkOps" description="Platform identity, versioning, and product context." /></CardBody></Card>
      </section>
    </>
  );
}
