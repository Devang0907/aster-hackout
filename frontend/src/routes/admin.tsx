import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { get } from "@/lib/api";
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
  const [statistics, setStatistics] = useState<{ userCount: number; reportingPeriodCount: number } | null>(null);
  const [error, setError] = useState("");

  const load = async () => {
    const [usersResponse, factoriesResponse, statisticsResponse] = await Promise.all([
      get("/api/v1/admin/users"),
      get("/api/v1/admin/factories"),
      get("/api/v1/admin/statistics"),
    ]);
    if (!usersResponse.ok || !factoriesResponse.ok || !statisticsResponse.ok) throw new Error("Unable to load admin data");
    setUsers(await usersResponse.json());
    setFactories(await factoriesResponse.json());
    setStatistics(await statisticsResponse.json());
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


  return (
    <div className="min-h-screen bg-background p-6 text-primary sm:p-10">
      <div className="mx-auto max-w-7xl">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-primary">
            Administration
          </p>
          <h1 className="mt-2 text-3xl font-semibold">Platform control</h1>
          <p className="mt-2 text-sm text-muted-foreground">
            Manage users and factories across CarbonLoop.
          </p>
        </div>
        {error && (
          <div className="mt-6 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
            {error}
          </div>
        )}
        {statistics && (
          <div className="mt-8 grid gap-6 lg:grid-cols-2">
            <section className="rounded-2xl border border-border bg-surface p-6 shadow-sm">
              <h2 className="text-xl font-semibold">Total Users</h2>
              <p className="mt-4 text-4xl font-bold text-primary">{statistics.userCount}</p>
            </section>
            <section className="rounded-2xl border border-border bg-surface p-6 shadow-sm">
              <h2 className="text-xl font-semibold">Practice Data (Reporting Periods)</h2>
              <p className="mt-4 text-4xl font-bold text-primary">{statistics.reportingPeriodCount}</p>
            </section>
          </div>
        )}
        <div className="mt-8 grid gap-6 lg:grid-cols-2">
          <section className="rounded-2xl border border-border bg-surface p-6 shadow-sm">
            <h2 className="text-xl font-semibold">Users</h2>
            <div className="mt-5 space-y-3">
              {users.map((user) => (
                <article
                  key={user.id}
                  className="flex items-center gap-4 rounded-xl border border-border bg-background p-4"
                >
                  <div>
                    <p className="font-medium">{user.fullName}</p>
                    <p className="text-xs text-muted-foreground">
                      {user.email} · {user.role}
                    </p>
                  </div>
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
                  className="flex items-center gap-4 rounded-xl border border-border bg-background p-4"
                >
                  <div>
                    <p className="font-medium">{factory.name}</p>
                    <p className="text-xs text-muted-foreground">
                      {factory.industryType} · {factory.isActive ? "Active" : "Inactive"}
                    </p>
                  </div>
                </article>
              ))}
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}
