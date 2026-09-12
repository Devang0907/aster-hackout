import { useState } from "react";
import { post } from "@/lib/api";

export function ManagerAccountForm({ factoryId }: { factoryId: string }) {
  const [form, setForm] = useState({ fullName: "", email: "", password: "" });
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const inputClass =
    "mt-2 w-full rounded-lg border border-border bg-background px-3 py-2 text-sm text-primary";

  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    setMessage("");
    setError("");
    setLoading(true);
    try {
      const response = await post(`/api/v1/factories/${factoryId}/manager`, { manager: form });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Unable to create manager account");
      setMessage(
        "Manager account created. Share the email and password securely with the manager.",
      );
      setForm({ fullName: "", email: "", password: "" });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to create manager account");
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="rounded-2xl border border-border bg-surface p-6 shadow-sm">
      <p className="text-xs font-semibold uppercase tracking-[0.18em] text-primary">
        Factory access
      </p>
      <h2 className="mt-2 text-xl font-semibold text-primary">Create factory manager</h2>
      <p className="mt-2 text-sm text-muted-foreground">
        One manager can be assigned to this factory. The manager signs in with these credentials.
      </p>
      {message && (
        <div className="mt-4 rounded-lg border border-green-200 bg-green-50 p-3 text-sm text-green-700">
          {message}
        </div>
      )}
      {error && (
        <div className="mt-4 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
          {error}
        </div>
      )}
      <form onSubmit={submit} className="mt-5 grid gap-4 sm:grid-cols-3">
        <label className="text-sm font-medium text-secondary">
          Full name
          <input
            className={inputClass}
            value={form.fullName}
            onChange={(e) => setForm({ ...form, fullName: e.target.value })}
            required
          />
        </label>
        <label className="text-sm font-medium text-secondary">
          Email
          <input
            className={inputClass}
            type="email"
            value={form.email}
            onChange={(e) => setForm({ ...form, email: e.target.value })}
            required
          />
        </label>
        <label className="text-sm font-medium text-secondary">
          Temporary password
          <input
            className={inputClass}
            type="password"
            minLength={8}
            value={form.password}
            onChange={(e) => setForm({ ...form, password: e.target.value })}
            required
          />
        </label>
        <div className="sm:col-span-3">
          <button
            type="submit"
            disabled={loading}
            className="rounded-full bg-primary px-5 py-2.5 text-xs font-semibold uppercase tracking-[0.12em] text-primary-foreground disabled:opacity-50"
          >
            {loading ? "Creating..." : "Create manager account"}
          </button>
        </div>
      </form>
    </section>
  );
}
