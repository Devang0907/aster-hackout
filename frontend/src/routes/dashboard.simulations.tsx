import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { get, post } from "@/lib/api";
import { DecimalValue, formatKgCo2eAsTonnes } from "@/lib/emissions";
import { FactoryPageShell } from "@/components/dashboard/FactoryPageShell";

export const Route = createFileRoute("/dashboard/simulations")({ component: Simulations });

interface CarbonResult {
  id: string;
  netCo2e: DecimalValue;
  totalCo2e: DecimalValue;
}
interface Simulation {
  id: string;
  name: string;
  baselineCo2e: DecimalValue;
  resultingCo2e: DecimalValue;
  co2ReductionPercentage: number;
  estimatedCost?: number;
  estimatedSavings?: number;
  paybackMonths?: number;
}

function Simulations() {
  return (
    <FactoryPageShell title="Simulations">
      {(factory) => <SimulationContent factoryId={factory.id} />}
    </FactoryPageShell>
  );
}

function SimulationContent({ factoryId }: { factoryId: string }) {
  const [results, setResults] = useState<CarbonResult[]>([]);
  const [items, setItems] = useState<Simulation[]>([]);
  const [name, setName] = useState("Renewable energy scenario");
  const [reduction, setReduction] = useState("20");
  const [cost, setCost] = useState("");
  const [savings, setSavings] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const load = async () => {
    const [resultResponse, simulationResponse] = await Promise.all([
      get(`/api/v1/factories/${factoryId}/carbon-results`),
      get(`/api/v1/factories/${factoryId}/simulations`),
    ]);
    if (resultResponse.ok) setResults(await resultResponse.json());
    if (simulationResponse.ok) setItems(await simulationResponse.json());
    setLoading(false);
  };

  useEffect(() => {
    load().catch(() => setLoading(false));
  }, [factoryId]);

  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    setError("");
    const base = Number(results[0]?.netCo2e ?? results[0]?.totalCo2e ?? 0);
    const percentage = Number(reduction);
    const reduced = (base * percentage) / 100;
    setSaving(true);
    try {
      if (!results[0]) throw new Error("Run an emissions analysis before creating a simulation");
      const response = await post(`/api/v1/factories/${factoryId}/simulations`, {
        baseResultId: results[0].id,
        name,
        assumptions: { reductionPercentage: percentage, basis: "user scenario" },
        baselineCo2e: base,
        resultingCo2e: base - reduced,
        co2Reduction: reduced,
        co2ReductionPercentage: percentage,
        ...(cost ? { estimatedCost: Number(cost) } : {}),
        ...(savings ? { estimatedSavings: Number(savings) } : {}),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Unable to save simulation");
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to save simulation");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-6">
      <section className="rounded-2xl border border-border bg-surface p-6 shadow-sm sm:p-8">
        <p className="text-xs font-semibold uppercase tracking-[0.18em] text-primary">What if?</p>
        <h1 className="mt-2 text-2xl font-semibold text-primary">Model a reduction scenario</h1>
        <p className="mt-2 text-sm leading-6 text-muted-foreground">
          Use your latest measured footprint as the baseline and compare a potential reduction.
        </p>
        {error && (
          <div className="mt-5 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
            {error}
          </div>
        )}
        <form onSubmit={submit} className="mt-6 grid gap-4 sm:grid-cols-2">
          <label className="text-sm font-medium text-secondary sm:col-span-2">
            Scenario name
            <input
              className="mt-2 w-full rounded-lg border border-border bg-background px-3 py-2.5 text-sm"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
          </label>
          <label className="text-sm font-medium text-secondary">
            Expected CO2 reduction (%)
            <input
              className="mt-2 w-full rounded-lg border border-border bg-background px-3 py-2.5 text-sm"
              type="number"
              min="0"
              max="100"
              step="any"
              value={reduction}
              onChange={(e) => setReduction(e.target.value)}
              required
            />
          </label>
          <label className="text-sm font-medium text-secondary">
            Estimated cost
            <input
              className="mt-2 w-full rounded-lg border border-border bg-background px-3 py-2.5 text-sm"
              type="number"
              min="0"
              step="any"
              value={cost}
              onChange={(e) => setCost(e.target.value)}
            />
          </label>
          <label className="text-sm font-medium text-secondary">
            Estimated annual savings
            <input
              className="mt-2 w-full rounded-lg border border-border bg-background px-3 py-2.5 text-sm"
              type="number"
              min="0"
              step="any"
              value={savings}
              onChange={(e) => setSavings(e.target.value)}
            />
          </label>
          <div className="sm:col-span-2">
            <button
              type="submit"
              disabled={saving || loading}
              className="rounded-full bg-primary px-5 py-2.5 text-xs font-semibold uppercase tracking-[0.12em] text-primary-foreground disabled:opacity-50"
            >
              {saving ? "Saving scenario..." : "Save simulation"}
            </button>
          </div>
        </form>
      </section>
      <section className="rounded-2xl border border-border bg-surface p-6 shadow-sm">
        <h2 className="text-xl font-semibold text-primary">Saved scenarios</h2>
        {items.length === 0 ? (
          <p className="mt-4 text-sm text-muted-foreground">No simulations saved yet.</p>
        ) : (
          <div className="mt-5 grid gap-3 sm:grid-cols-2">
            {items.map((item) => (
              <article key={item.id} className="rounded-xl border border-border bg-background p-4">
                <p className="font-medium text-primary">{item.name}</p>
                <p className="mt-2 text-sm text-secondary">
                  {Number(item.co2ReductionPercentage).toFixed(1)}% reduction ·{" "}
                  {formatKgCo2eAsTonnes(item.resultingCo2e)} remaining
                </p>
                {item.estimatedSavings != null && (
                  <p className="mt-1 text-xs text-muted-foreground">
                    Estimated savings: {Number(item.estimatedSavings).toLocaleString()}
                  </p>
                )}
              </article>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
