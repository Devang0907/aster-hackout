import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { get } from "@/lib/api";
import { DecimalValue, formatKgCo2eAsTonnes } from "@/lib/emissions";
import { FactoryPageShell } from "@/components/dashboard/FactoryPageShell";

export const Route = createFileRoute("/dashboard/leak-points")({ component: LeakPoints });

interface EmissionSource {
  id: string;
  sourceName: string;
  emissionsCo2e: DecimalValue;
  percentage: DecimalValue;
  severity: string;
  rank: number;
  explanation?: string;
}

function LeakPoints() {
  return (
    <FactoryPageShell title="Leak Points">
      {(factory) => <LeakPointContent factoryId={factory.id} />}
    </FactoryPageShell>
  );
}

function LeakPointContent({ factoryId }: { factoryId: string }) {
  const [sources, setSources] = useState<EmissionSource[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    setLoading(true);
    setError("");
    get(`/api/v1/factories/${factoryId}/carbon-results`)
      .then(async (response) => {
        const results = await response.json();
        if (!response.ok) throw new Error(results.detail || "Unable to load leak points");
        setSources(
          [...(results[0]?.emissionSources || [])].sort(
            (left: EmissionSource, right: EmissionSource) => left.rank - right.rank,
          ),
        );
      })
      .catch((caught) =>
        setError(caught instanceof Error ? caught.message : "Unable to load leak points"),
      )
      .finally(() => setLoading(false));
  }, [factoryId]);

  return (
    <section className="rounded-2xl border border-border bg-surface p-6 shadow-sm sm:p-8">
      <p className="text-xs font-semibold uppercase tracking-[0.18em] text-primary">
        Where to focus
      </p>
      <h1 className="mt-2 text-2xl font-semibold text-primary">Emission leak points</h1>
      <p className="mt-2 text-sm leading-6 text-muted-foreground">
        The latest calculation ranked by contribution to your factory footprint.
      </p>
      {loading ? (
        <div className="mt-6 h-32 animate-pulse rounded-xl bg-mist" />
      ) : error || sources.length === 0 ? (
        <p className={`mt-6 text-sm ${error ? "text-red-700" : "text-muted-foreground"}`}>
          {error || "Run an emissions analysis to identify leak points."}
        </p>
      ) : (
        <div className="mt-6 space-y-3">
          {sources.map((source) => (
            <article key={source.id} className="rounded-xl border border-border bg-background p-4">
              <div className="flex items-center justify-between gap-4">
                <div>
                  <h2 className="font-medium text-primary">{source.sourceName}</h2>
                  <p className="mt-1 text-xs text-muted-foreground">
                    {source.severity} severity · {Number(source.percentage).toFixed(1)}% of total
                  </p>
                </div>
                <p className="text-lg font-semibold text-primary">
                  {formatKgCo2eAsTonnes(source.emissionsCo2e)}
                </p>
              </div>
              {source.explanation && (
                <p className="mt-3 text-sm text-secondary">{source.explanation}</p>
              )}
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
