import { DashboardLayout } from "@/components/layout/DashboardLayout";

const Billing = () => {
  return (
    <DashboardLayout>
      <div className="space-y-6">
        <h1 className="text-3xl font-bold text-foreground">Billing</h1>
        <div className="bg-card border border-border rounded-lg p-8 text-center">
          <h2 className="text-xl font-semibold text-foreground mb-4">Billing Management</h2>
          <p className="text-muted-foreground">
            Manage your subscription, payment methods, and billing history.
          </p>
          <div className="mt-6 text-sm text-muted-foreground">
            Coming soon...
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
};

export default Billing;