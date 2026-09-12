import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { get, patch } from "@/lib/api";
import { getUser } from "@/lib/auth";

export const Route = createFileRoute("/admin")({ component: Admin });

interface UserRecord {
  id: string;
  fullName: string;
  email: string;
  role: string;
  isActive: boolean;
}
interface FactoryRecord {
  id: string;
  name: string;
  ownerId: string;
  managerId?: string;
  industryType: string;
  isActive: boolean;
}

function Admin() {
  const navigate = useNavigate();
  const [users, setUsers] = useState<UserRecord[]>([]);
  const [factories, setFactories] = useState<FactoryRecord[]>([]);
  const [error, setError] = useState("");

  const load = async () => {
    const [usersResponse, factoriesResponse] = await Promise.all([
      get("/api/v1/admin/users"),
      get("/api/v1/admin/factories"),
    ]);
    if (!usersResponse.ok || !factoriesResponse.ok) throw new Error("Unable to load admin data");
    setUsers(await usersResponse.json());
    setFactories(await factoriesResponse.json());
  };

  useEffect(() => {
    if (getUser()?.role !== "admin") {
      navigate({ to: "/dashboard" });
      return;
    }
    load().catch((err) =>
      setError(err instanceof Error ? err.message : "Unable to load admin data"),
    );
  }, [navigate]);

  const toggleUser = async (user: UserRecord) => {
    await patch(`/api/v1/admin/users/${user.id}/active?active=${!user.isActive}`, {});
    await load();
  };

  const toggleFactory = async (factory: FactoryRecord) => {
    await patch(`/api/v1/admin/factories/${factory.id}/active?active=${!factory.isActive}`, {});
    await load();
  };

  return (
    <div className="min-h-screen bg-background p-6 text-primary sm:p-10">
      <div className="mx-auto max-w-7xl">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-primary">
              Administration
            </p>
            <h1 className="mt-2 text-3xl font-semibold">Platform control</h1>
            <p className="mt-2 text-sm text-muted-foreground">
              Manage users and factories across CarbonLoop.
            </p>
          </div>
          <button
            onClick={() => navigate({ to: "/dashboard" })}
            className="rounded-full border border-border px-4 py-2 text-xs font-semibold uppercase tracking-[0.12em] text-secondary"
          >
            Back to dashboard
          </button>
        </div>
        {error && (
          <div className="mt-6 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
            {error}
          </div>
        )}
        <div className="mt-8 grid gap-6 lg:grid-cols-2">
          <section className="rounded-2xl border border-border bg-surface p-6 shadow-sm">
            <h2 className="text-xl font-semibold">Users</h2>
            <div className="mt-5 space-y-3">
              {users.map((user) => (
                <article
                  key={user.id}
                  className="flex items-center justify-between gap-4 rounded-xl border border-border bg-background p-4"
                >
                  <div>
                    <p className="font-medium">{user.fullName}</p>
                    <p className="text-xs text-muted-foreground">
                      {user.email} · {user.role}
                    </p>
                  </div>
                  <button
                    onClick={() => toggleUser(user)}
                    className="rounded-full border border-border px-3 py-1 text-xs font-medium"
                  >
                    {user.isActive ? "Deactivate" : "Activate"}
                  </button>
                </article>
              ))}
            </div>
          </section>
          <section className="rounded-2xl border border-border bg-surface p-6 shadow-sm">
            <h2 className="text-xl font-semibold">Factories</h2>
            <div className="mt-5 space-y-3">
              {factories.map((factory) => (
                <article
                  key={factory.id}
                  className="flex items-center justify-between gap-4 rounded-xl border border-border bg-background p-4"
                >
                  <div>
                    <p className="font-medium">{factory.name}</p>
                    <p className="text-xs text-muted-foreground">
                      {factory.industryType} · {factory.isActive ? "Active" : "Inactive"}
                    </p>
                  </div>
                  <button
                    onClick={() => toggleFactory(factory)}
                    className="rounded-full border border-border px-3 py-1 text-xs font-medium"
                  >
                    {factory.isActive ? "Deactivate" : "Activate"}
                  </button>
                </article>
              ))}
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}
