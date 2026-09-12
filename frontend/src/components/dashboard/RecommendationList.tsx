import { useEffect, useState } from "react";
import { get, patch } from "@/lib/api";

interface Recommendation {
  id: string;
  priority: number;
  status: string;
  estimatedCo2Reduction?: number;
  estimatedCost?: number;
  paybackMonths?: number;
  aiExplanation?: string;
  intervention?: { name?: string; category?: string };
}

interface RecommendationListProps {
  factoryId: string;
}

export function RecommendationList({ factoryId }: RecommendationListProps) {
  const [items, setItems] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    try {
      const response = await get(`/api/v1/factories/${factoryId}/recommendations`);
      if (response.ok) setItems(await response.json());
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    async function fetchRecommendations() {
      try {
        const response = await get(`/api/v1/factories/${factoryId}/recommendations`);
        if (response.ok) setItems(await response.json());
      } finally {
        setLoading(false);
      }
    }

    fetchRecommendations();
  }, [factoryId]);

  const updateStatus = async (id: string, status: "viewed" | "accepted" | "rejected") => {
    const response = await patch(`/api/v1/factories/${factoryId}/recommendations/${id}`, {
      status,
    });
    if (response.ok) load();
  };

  return (
    <section className="rounded-2xl border border-border bg-surface p-6 shadow-sm">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-primary">
            Next actions
          </p>
          <h2 className="mt-2 text-xl font-semibold text-primary">Recommendations</h2>
        </div>
        <span className="rounded-full bg-mist px-3 py-1 text-xs font-medium text-secondary">
          {items.length} active
        </span>
      </div>

      {loading ? (
        <div className="mt-6 space-y-3">
          <div className="h-16 animate-pulse rounded-lg bg-mist" />
          <div className="h-16 animate-pulse rounded-lg bg-mist" />
        </div>
      ) : items.length === 0 ? (
        <p className="mt-6 text-sm text-muted-foreground">
          Run an emissions analysis to receive prioritized actions.
        </p>
      ) : (
        <div className="mt-6 space-y-3">
          {items.slice(0, 5).map((item) => (
            <article key={item.id} className="rounded-xl border border-border bg-background p-4">
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <p className="font-medium text-primary">
                    {item.intervention?.name || "Sustainability intervention"}
                  </p>
                  <p className="mt-1 text-xs uppercase tracking-[0.12em] text-muted-foreground">
                    Priority {item.priority} · {item.intervention?.category || "operations"}
                  </p>
                </div>
                <span className="text-sm font-semibold text-primary">
                  {item.estimatedCo2Reduction
                    ? `${Number(item.estimatedCo2Reduction).toFixed(1)} t CO2e`
                    : "Impact pending"}
                </span>
              </div>
              {item.aiExplanation && (
                <p className="mt-3 text-sm leading-5 text-secondary">{item.aiExplanation}</p>
              )}
              <div className="mt-4 flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
                {item.estimatedCost != null && (
                  <span>Cost: {Number(item.estimatedCost).toLocaleString()}</span>
                )}
                {item.paybackMonths != null && (
                  <span>Payback: {Number(item.paybackMonths).toFixed(1)} months</span>
                )}
                <button
                  onClick={() => updateStatus(item.id, "accepted")}
                  className="ml-auto rounded-full border border-primary px-3 py-1 font-medium text-primary hover:bg-primary hover:text-primary-foreground"
                >
                  Accept
                </button>
                <button
                  onClick={() => updateStatus(item.id, "rejected")}
                  className="rounded-full border border-border px-3 py-1 font-medium text-secondary hover:bg-mist"
                >
                  Dismiss
                </button>
              </div>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
