import { useEffect, useState } from "react";
import { get } from "@/lib/api";

interface DashboardSummary {
  totalCo2e: number;
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

  useEffect(() => {
    async function fetchSummary() {
      try {
        const response = await get(`/api/v1/factories/${factoryId}/dashboard-summary`);
        const data = await response.json();
        setSummary(data);
      } catch (error) {
        console.error("Failed to fetch dashboard summary:", error);
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

  const cards = [
    {
      title: "Total CO2e",
      value: summary?.totalCo2e?.toFixed(2) || "0.00",
      unit: "t",
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
    {
      title: "Simulations",
      value: summary?.simulationCount || 0,
      unit: "",
      color: "text-primary",
    },
  ];

  return (
    <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
      {cards.map((card) => (
        <div
          key={card.title}
          className="rounded-xl border border-border bg-surface p-6"
        >
          <p className="text-sm font-medium text-secondary">{card.title}</p>
          <p className={`mt-2 text-3xl font-semibold ${card.color}`}>
            {card.value}
            <span className="text-lg font-normal text-muted-foreground ml-1">
              {card.unit}
            </span>
          </p>
        </div>
      ))}
    </div>
  );
}
