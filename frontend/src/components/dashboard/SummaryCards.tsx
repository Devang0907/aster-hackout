import { useEffect, useState } from "react";
import { get } from "@/lib/api";
import { DecimalValue, formatTonnes } from "@/lib/emissions";

interface DashboardSummary {
  totalCo2e: DecimalValue;
  netCo2e: DecimalValue;
  carbonIntensity: DecimalValue;
  carbonIntensityUnit?: string;
  activeRecommendations: number;
  leakPoints: number;
  simulationCount: number;
}

interface SummaryCardsProps {
  factoryId: string;
}

export function SummaryCards({ factoryId }: SummaryCardsProps) {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function fetchSummary() {
      setLoading(true);
      setError("");
      try {
        const response = await get(`/api/v1/factories/${factoryId}/dashboard-summary`);
        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || "Unable to load dashboard summary");
        setSummary(data);
      } catch (caught) {
        setError(caught instanceof Error ? caught.message : "Unable to load dashboard summary");
      } finally {
        setLoading(false);
      }
    }

    fetchSummary();
  }, [factoryId]);

  if (loading) {
    return (
      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="h-32 rounded-xl border border-border bg-surface animate-pulse" />
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
        {error}
      </div>
    );
  }

  const cards = [
    {
      title: "Net footprint",
      value: formatTonnes(summary?.netCo2e ?? summary?.totalCo2e),
      unit: "t CO₂e",
      color: "text-primary",
    },
    {
      title: "Carbon intensity",
      value:
        summary?.carbonIntensity == null
          ? "—"
          : Number(summary.carbonIntensity).toLocaleString(undefined, {
              maximumFractionDigits: 2,
            }),
      unit: summary?.carbonIntensityUnit || "",
      color: "text-primary",
    },
    {
      title: "Active Recommendations",
      value: summary?.activeRecommendations || 0,
      unit: "",
      color: "text-primary",
    },
    {
      title: "Leak Points",
      value: summary?.leakPoints || 0,
      unit: "",
      color: "text-primary",
    },
    { title: "Simulations", value: summary?.simulationCount || 0, unit: "", color: "text-primary" },
  ];

  return (
    <div className="grid gap-6 sm:grid-cols-2 xl:grid-cols-5">
      {cards.map((card) => (
        <div
          key={card.title}
          className="rounded-xl border border-border bg-surface p-6 flex flex-col justify-between"
        >
          <p className="text-sm font-medium text-secondary">{card.title}</p>
          <div className="mt-4">
            <p className={`text-3xl font-semibold ${card.color}`}>
              {card.value}
              {card.unit && (
                <span className="text-lg font-normal text-muted-foreground ml-1">
                  {card.unit}
                </span>
              )}
            </p>
          </div>
        </div>
      ))}
    </div>
  );
}
