import { useState } from "react";
import { patch } from "@/lib/api";

export interface FactoryProfile {
  id: string;
  name: string;
  industryType?: string;
  description?: string;
  address?: string;
  city?: string;
  state?: string;
  country?: string;
  employees?: number;
  productionCapacity?: number;
  productionUnit?: string;
  establishedYear?: number;
}

interface FactoryProfileFormProps {
  factory: FactoryProfile;
  onUpdated: (factory: FactoryProfile) => void;
}

export function FactoryProfileForm({ factory, onUpdated }: FactoryProfileFormProps) {
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({
    name: factory.name || "",
    industryType: factory.industryType || "",
    description: factory.description || "",
    address: factory.address || "",
    city: factory.city || "",
    state: factory.state || "",
    country: factory.country || "India",
    employees: factory.employees?.toString() || "",
    productionCapacity: factory.productionCapacity?.toString() || "",
    productionUnit: factory.productionUnit || "",
    establishedYear: factory.establishedYear?.toString() || "",
  });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  const update = (field: keyof typeof form, value: string) =>
    setForm((current) => ({ ...current, [field]: value }));

  const save = async (event: React.FormEvent) => {
    event.preventDefault();
    setSaving(true);
    setError("");
    try {
      const response = await patch(`/api/v1/factories/${factory.id}`, {
        name: form.name,
        industryType: form.industryType,
        description: form.description || null,
        address: form.address || null,
        city: form.city,
        state: form.state,
        country: form.country,
        employees: form.employees ? Number(form.employees) : null,
        productionCapacity: form.productionCapacity ? Number(form.productionCapacity) : null,
        productionUnit: form.productionUnit || null,
        establishedYear: form.establishedYear ? Number(form.establishedYear) : null,
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Unable to update factory profile");
      onUpdated(data);
      setOpen(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to update factory profile");
    } finally {
      setSaving(false);
    }
  };

  const inputClass =
    "w-full rounded-lg border border-border bg-background px-3 py-2 text-sm text-primary focus:outline-none focus:ring-2 focus:ring-primary/40";

  return (
    <section className="rounded-2xl border border-border bg-surface p-6 shadow-sm">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-primary">
            Factory profile
          </p>
          <h2 className="mt-2 text-xl font-semibold text-primary">{factory.name}</h2>
          <p className="mt-1 text-sm text-muted-foreground">
            {factory.industryType} · {factory.city}, {factory.state}
          </p>
        </div>
        <button
          type="button"
          onClick={() => setOpen(!open)}
          className="rounded-full border border-border px-4 py-2 text-xs font-semibold uppercase tracking-[0.12em] text-secondary hover:bg-mist"
        >
          {open ? "Close editor" : "Edit profile"}
        </button>
      </div>

      {open && (
        <form
          onSubmit={save}
          className="mt-6 grid gap-4 border-t border-border pt-6 sm:grid-cols-2"
        >
          {error && (
            <div className="sm:col-span-2 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
              {error}
            </div>
          )}
          <label className="text-sm font-medium text-secondary">
            Factory name
            <input
              className={`${inputClass} mt-2`}
              value={form.name}
              onChange={(e) => update("name", e.target.value)}
              required
            />
          </label>
          <label className="text-sm font-medium text-secondary">
            Industry
            <input
              className={`${inputClass} mt-2`}
              value={form.industryType}
              onChange={(e) => update("industryType", e.target.value)}
              required
            />
          </label>
          <label className="text-sm font-medium text-secondary sm:col-span-2">
            Description
            <textarea
              className={`${inputClass} mt-2 min-h-20`}
              value={form.description}
              onChange={(e) => update("description", e.target.value)}
            />
          </label>
          <label className="text-sm font-medium text-secondary sm:col-span-2">
            Address
            <input
              className={`${inputClass} mt-2`}
              value={form.address}
              onChange={(e) => update("address", e.target.value)}
            />
          </label>
          <label className="text-sm font-medium text-secondary">
            City
            <input
              className={`${inputClass} mt-2`}
              value={form.city}
              onChange={(e) => update("city", e.target.value)}
              required
            />
          </label>
          <label className="text-sm font-medium text-secondary">
            State
            <input
              className={`${inputClass} mt-2`}
              value={form.state}
              onChange={(e) => update("state", e.target.value)}
              required
            />
          </label>
          <label className="text-sm font-medium text-secondary">
            Country
            <input
              className={`${inputClass} mt-2`}
              value={form.country}
              onChange={(e) => update("country", e.target.value)}
              required
            />
          </label>
          <label className="text-sm font-medium text-secondary">
            Established year
            <input
              className={`${inputClass} mt-2`}
              type="number"
              min="1"
              value={form.establishedYear}
              onChange={(e) => update("establishedYear", e.target.value)}
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
            Production capacity
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
              value={form.productionUnit}
              onChange={(e) => update("productionUnit", e.target.value)}
            />
          </label>
          <div className="sm:col-span-2">
            <button
              type="submit"
              disabled={saving}
              className="rounded-full bg-primary px-5 py-2.5 text-xs font-semibold uppercase tracking-[0.12em] text-primary-foreground disabled:opacity-50"
            >
              {saving ? "Saving..." : "Save profile"}
            </button>
          </div>
        </form>
      )}
    </section>
  );
}
