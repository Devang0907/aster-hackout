import { useEffect, useState } from "react";
import { get } from "@/lib/api";
import {
  DecimalValue,
  decimalNumber,
  formatKgCo2eAsTonnes,
} from "@/lib/emissions";

interface EmissionSource {
  id: string;
  sourceName: string;
  emissionsCo2e: DecimalValue;
  percentage: DecimalValue;
  severity: string;
  rank: number;
}

interface CarbonResult {
  id: string;
  totalCo2e: DecimalValue;
  netCo2e: DecimalValue;
  carbonIntensity: DecimalValue;
  carbonIntensityUnit?: string;
  calculationVersion: string;
  calculatedAt: string;
  emissionSources: EmissionSource[];
}

export function LatestEmissionBreakdown({ factoryId }: { factoryId: string }) {
  const [result, setResult] = useState<CarbonResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadLatestResult() {
      setLoading(true);
      setError("");
      try {
        const response = await get(`/api/v1/factories/${factoryId}/carbon-results`);
        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || "Unable to load the latest footprint");
        setResult(data[0] || null);
      } catch (caught) {
        setError(caught instanceof Error ? caught.message : "Unable to load the latest footprint");
      } finally {
        setLoading(false);
      }
    }

    void loadLatestResult();
  }, [factoryId]);

  if (loading) {
    return <div className="h-64 animate-pulse rounded-2xl border border-border bg-surface" />;
  }

  if (error || !result) {
    return (
      <section className="rounded-2xl border border-border bg-surface p-6 shadow-sm">
        <h2 className="text-xl font-semibold text-primary">Latest emission breakdown</h2>
        <p className={`mt-3 text-sm ${error ? "text-red-700" : "text-muted-foreground"}`}>
          {error || "Run an emissions analysis to see the calculated category breakdown."}
        </p>
      </section>
    );
  }

  const sources = [...(result.emissionSources || [])].sort(
    (left, right) => left.rank - right.rank,
  );

  return (
    <section className="rounded-2xl border border-border bg-surface p-6 shadow-sm sm:p-8">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-primary">
            Calculated output
          </p>
          <h2 className="mt-2 text-2xl font-semibold text-primary">Latest emission breakdown</h2>
          <p className="mt-2 text-sm text-muted-foreground">
            {new Date(result.calculatedAt).toLocaleDateString()} · calculation v
            {result.calculationVersion}
          </p>
        </div>
        <div className="rounded-xl bg-mist px-5 py-3 text-right">
          <p className="text-xs uppercase tracking-[0.12em] text-muted-foreground">Net footprint</p>
          <p className="mt-1 text-xl font-semibold text-primary">
            {formatKgCo2eAsTonnes(result.netCo2e)}
          </p>
        </div>
      </div>

      <div className="mt-7 grid gap-3 md:grid-cols-2 xl:grid-cols-5">
        {sources.map((source) => {
          const percentage = decimalNumber(source.percentage);
          return (
            <article key={source.id} className="rounded-xl border border-border bg-background p-4">
              <div className="flex items-center justify-between gap-3">
                <h3 className="font-medium text-primary">{source.sourceName}</h3>
                <span className="text-xs capitalize text-muted-foreground">{source.severity}</span>
              </div>
              <p className="mt-3 text-lg font-semibold text-primary">
                {formatKgCo2eAsTonnes(source.emissionsCo2e)}
              </p>
              <div className="mt-3 h-1.5 overflow-hidden rounded-full bg-mist">
                <div
                  className="h-full rounded-full bg-primary"
                  style={{ width: `${Math.min(100, Math.max(0, percentage))}%` }}
                />
              </div>
              <p className="mt-2 text-xs text-muted-foreground">
                {percentage.toFixed(2)}% of gross emissions
              </p>
            </article>
          );
        })}
      </div>

      <div className="mt-6 flex flex-wrap gap-x-8 gap-y-2 border-t border-border pt-5 text-sm text-secondary">
        <span>Gross: {formatKgCo2eAsTonnes(result.totalCo2e)}</span>
        {result.carbonIntensity != null && (
          <span>
            Intensity: {decimalNumber(result.carbonIntensity).toFixed(2)} {result.carbonIntensityUnit}
          </span>
        )}
      </div>
    </section>
  );
}
