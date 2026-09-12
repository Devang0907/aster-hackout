import { useEffect, useState, type ReactNode } from "react";
import { get } from "@/lib/api";
import { ProtectedRoute } from "@/components/ProtectedRoute";
import { DashboardLayout } from "@/components/dashboard/DashboardLayout";
import { FactoryOnboarding } from "@/components/dashboard/FactoryOnboarding";
import type { FactoryProfile } from "@/components/dashboard/FactoryProfileForm";
import { getSelectedFactoryId } from "@/lib/factory";

interface FactoryPageShellProps {
  title: string;
  children: (factory: FactoryProfile, refresh: () => void) => ReactNode;
}

export function FactoryPageShell({ title, children }: FactoryPageShellProps) {
  const [factory, setFactory] = useState<FactoryProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadFactory = async () => {
    setError("");
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
      <DashboardLayout title={title}>
        {loading ? (
          <div className="h-56 animate-pulse rounded-2xl bg-mist" />
        ) : error ? (
          <div className="rounded-xl border border-red-200 bg-red-50 p-5 text-sm text-red-700">
            {error}
          </div>
        ) : !factory ? (
          <FactoryOnboarding onCreated={(created) => setFactory(created)} />
        ) : (
          children(factory, loadFactory)
        )}
      </DashboardLayout>
    </ProtectedRoute>
  );
}
