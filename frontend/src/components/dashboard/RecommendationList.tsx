import { useCallback, useEffect, useState } from "react";
import { get, patch } from "@/lib/api";
import { DecimalValue, formatKgCo2eAsTonnes } from "@/lib/emissions";

interface Recommendation {
  id: string;
  priority: number;
  status: string;
  recommendationScore?: DecimalValue;
  estimatedCo2Reduction?: DecimalValue;
  estimatedCost?: DecimalValue;
  estimatedAnnualSavings?: DecimalValue;
  paybackMonths?: DecimalValue;
  feasibilityScore?: DecimalValue;
  aiExplanation?: string;
  intervention?: { name?: string; category?: string };
}

interface RecommendationListProps {
  factoryId: string;
  onStatusChanged?: () => void;
}

export function RecommendationList({ factoryId, onStatusChanged }: RecommendationListProps) {
  const [items, setItems] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const response = await get(`/api/v1/factories/${factoryId}/recommendations`);
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Unable to load recommendations");
      setItems(data);
    } catch (caught) {
      setItems([]);
      setError(caught instanceof Error ? caught.message : "Unable to load recommendations");
    } finally {
      setLoading(false);
    }
  }, [factoryId]);

  useEffect(() => {
    void load();
  }, [load]);

  const updateStatus = async (id: string, status: "viewed" | "accepted" | "rejected") => {
    const response = await patch(`/api/v1/factories/${factoryId}/recommendations/${id}`, {
      status,
    });
    if (response.ok) {
      await load();
      onStatusChanged?.();
    }
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
        <p className={`mt-6 text-sm ${error ? "text-red-700" : "text-muted-foreground"}`}>
          {error || "Run an emissions analysis to receive prioritized actions."}
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
                    ? formatKgCo2eAsTonnes(item.estimatedCo2Reduction)
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
                {item.estimatedAnnualSavings != null && (
                  <span>Savings/year: {Number(item.estimatedAnnualSavings).toLocaleString()}</span>
                )}
                {item.paybackMonths != null && (
                  <span>Payback: {Number(item.paybackMonths).toFixed(1)} months</span>
                )}
                {item.recommendationScore != null && (
                  <span>Score: {Number(item.recommendationScore).toFixed(1)}/100</span>
                )}
                {item.feasibilityScore != null && (
                  <span>Feasibility: {Number(item.feasibilityScore).toFixed(0)}%</span>
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
