import { createFileRoute } from "@tanstack/react-router";
import { ProtectedRoute } from "@/components/ProtectedRoute";
import { DashboardLayout } from "@/components/dashboard/DashboardLayout";
import { SummaryCards } from "@/components/dashboard/SummaryCards";
import { RecentActivity } from "@/components/dashboard/RecentActivity";

export const Route = createFileRoute("/dashboard")({
  component: Dashboard,
});

function Dashboard() {
  // For now, use a placeholder factory ID
  // This will be replaced with the selected factory from context
  const factoryId = "placeholder-factory-id";

  return (
    <ProtectedRoute>
      <DashboardLayout>
        <div className="space-y-6">
          <SummaryCards factoryId={factoryId} />
          <RecentActivity factoryId={factoryId} />
        </div>
      </DashboardLayout>
    </ProtectedRoute>
  );
}
