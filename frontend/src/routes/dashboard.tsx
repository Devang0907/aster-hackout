import { createFileRoute, Outlet, useRouterState } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { get } from "@/lib/api";
import { ProtectedRoute } from "@/components/ProtectedRoute";
import { DashboardLayout } from "@/components/dashboard/DashboardLayout";
import { FactoryOnboarding } from "@/components/dashboard/FactoryOnboarding";
import { FactoryProfileForm, FactoryProfile } from "@/components/dashboard/FactoryProfileForm";
import { EmissionsAnalysisForm } from "@/components/dashboard/EmissionsAnalysisForm";
import { RecommendationList } from "@/components/dashboard/RecommendationList";
import { SummaryCards } from "@/components/dashboard/SummaryCards";
import { RecentActivity } from "@/components/dashboard/RecentActivity";
import { getSelectedFactoryId } from "@/lib/factory";

export const Route = createFileRoute("/dashboard")({
  component: Dashboard,
});

function Dashboard() {
  const pathname = useRouterState({ select: (state) => state.location.pathname });
  const [factory, setFactory] = useState<FactoryProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [analysisVersion, setAnalysisVersion] = useState(0);

  const loadFactory = async () => {
    try {
      const response = await get("/api/v1/factories");
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Unable to load factory");
      const selectedId = getSelectedFactoryId();
      setFactory(data.find((item: FactoryProfile) => item.id === selectedId) || data[0] || null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to load factory");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadFactory();
    const handleFactoryChange = () => loadFactory();
    window.addEventListener("factory-changed", handleFactoryChange);
    return () => window.removeEventListener("factory-changed", handleFactoryChange);
  }, []);

  return (
    <ProtectedRoute>
      {pathname !== "/dashboard" ? (
        <Outlet />
      ) : (
        <DashboardLayout>
          {loading ? (
            <div className="h-56 animate-pulse rounded-2xl bg-mist" />
          ) : error ? (
            <div className="rounded-xl border border-red-200 bg-red-50 p-5 text-sm text-red-700">
              {error}
            </div>
          ) : !factory ? (
            <FactoryOnboarding onCreated={(created) => setFactory(created)} />
          ) : (
            <div className="space-y-6">
              <FactoryProfileForm factory={factory} onUpdated={setFactory} />
              <SummaryCards key={`summary-${analysisVersion}`} factoryId={factory.id} />
              <div className="grid gap-6 xl:grid-cols-[minmax(0,1.25fr)_minmax(320px,0.75fr)]">
                <EmissionsAnalysisForm
                  factoryId={factory.id}
                  onComplete={() => setAnalysisVersion((version) => version + 1)}
                />
                <RecommendationList
                  key={`recommendations-${analysisVersion}`}
                  factoryId={factory.id}
                />
              </div>
              <RecentActivity key={`activity-${analysisVersion}`} factoryId={factory.id} />
            </div>
          )}
        </DashboardLayout>
      )}
    </ProtectedRoute>
  );
}
