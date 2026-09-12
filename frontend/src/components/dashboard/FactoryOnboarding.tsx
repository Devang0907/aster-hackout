import { useState } from "react";
import { post } from "@/lib/api";

interface FactoryOnboardingProps {
  onCreated: (factory: { id: string; name: string }) => void;
  onCancel?: () => void;
}

export function FactoryOnboarding({ onCreated, onCancel }: FactoryOnboardingProps) {
  const [form, setForm] = useState({
    name: "",
    industryType: "",
    city: "",
    state: "",
    country: "India",
    employees: "",
    productionCapacity: "",
    productionUnit: "",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const update = (field: keyof typeof form, value: string) => {
    setForm((current) => ({ ...current, [field]: value }));
  };

  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    setError("");
    setLoading(true);

    try {
      const response = await post("/api/v1/factories", {
        name: form.name,
        industryType: form.industryType,
        city: form.city,
        state: form.state,
        country: form.country,
        ...(form.employees ? { employees: Number(form.employees) } : {}),
        ...(form.productionCapacity ? { productionCapacity: Number(form.productionCapacity) } : {}),
        ...(form.productionUnit ? { productionUnit: form.productionUnit } : {}),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Unable to create factory");
      onCreated(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to create factory");
    } finally {
      setLoading(false);
    }
  };

  const inputClass =
    "w-full rounded-lg border border-border bg-background px-3 py-2.5 text-sm text-primary focus:outline-none focus:ring-2 focus:ring-primary/40";

  return (
    <section className="relative mx-auto max-w-4xl rounded-2xl border border-border bg-surface p-6 shadow-sm sm:p-8">
      {onCancel && (
        <button
          type="button"
          onClick={onCancel}
          className="absolute right-6 top-6 rounded-full border border-border px-4 py-2 text-xs font-semibold uppercase tracking-[0.12em] text-secondary hover:bg-mist"
        >
          Cancel
        </button>
      )}
      <div className="mb-8 max-w-2xl">
        <p className="text-xs font-semibold uppercase tracking-[0.18em] text-primary">
          {onCancel ? "Add new factory" : "First-login setup"}
        </p>
        <h1 className="mt-2 text-3xl font-semibold text-primary">Tell us about your factory</h1>
        <p className="mt-3 text-sm leading-6 text-muted-foreground">
          These essentials create your factory workspace. You can add addresses, capacity details,
          and other operational information from your factory profile later.
        </p>
      </div>

      {error && (
        <div className="mb-6 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
          {error}
        </div>
      )}

      <form onSubmit={submit} className="space-y-8">
        <div className="grid gap-5 sm:grid-cols-2">
          <label className="text-sm font-medium text-secondary">
            Factory name *
            <input
              className={`${inputClass} mt-2`}
              value={form.name}
              onChange={(e) => update("name", e.target.value)}
              required
            />
          </label>
          <label className="text-sm font-medium text-secondary">
            Industry *
            <input
              className={`${inputClass} mt-2`}
              placeholder="Textiles, metals, food..."
              value={form.industryType}
              onChange={(e) => update("industryType", e.target.value)}
              required
            />
          </label>
          <label className="text-sm font-medium text-secondary">
            City *
            <input
              className={`${inputClass} mt-2`}
              value={form.city}
              onChange={(e) => update("city", e.target.value)}
              required
            />
          </label>
          <label className="text-sm font-medium text-secondary">
            State or province *
            <input
              className={`${inputClass} mt-2`}
              value={form.state}
              onChange={(e) => update("state", e.target.value)}
              required
            />
          </label>
          <label className="text-sm font-medium text-secondary">
            Country *
            <input
              className={`${inputClass} mt-2`}
              value={form.country}
              onChange={(e) => update("country", e.target.value)}
              required
            />
          </label>
          <label className="text-sm font-medium text-secondary">
            Employees
            <input
              className={`${inputClass} mt-2`}
              type="number"
              min="0"
              value={form.employees}
              onChange={(e) => update("employees", e.target.value)}
            />
          </label>
          <label className="text-sm font-medium text-secondary">
            Annual production capacity
            <input
              className={`${inputClass} mt-2`}
              type="number"
              min="0"
              step="any"
              value={form.productionCapacity}
              onChange={(e) => update("productionCapacity", e.target.value)}
            />
          </label>
          <label className="text-sm font-medium text-secondary">
            Production unit
            <input
              className={`${inputClass} mt-2`}
              placeholder="tonnes/year"
              value={form.productionUnit}
              onChange={(e) => update("productionUnit", e.target.value)}
            />
          </label>
        </div>
        <button
          type="submit"
          disabled={loading}
          className="rounded-full bg-primary px-6 py-3 text-sm font-semibold uppercase tracking-[0.14em] text-primary-foreground transition-opacity hover:opacity-90 disabled:opacity-50"
        >
          {loading ? "Creating workspace..." : "Create factory workspace"}
        </button>
      </form>
    </section>
  );
}
