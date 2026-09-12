import { createFileRoute } from "@tanstack/react-router";
import { FactoryPageShell } from "@/components/dashboard/FactoryPageShell";
import { FactoryProfileForm } from "@/components/dashboard/FactoryProfileForm";
import { FactoryOnboarding } from "@/components/dashboard/FactoryOnboarding";
import { getUser } from "@/lib/auth";

export const Route = createFileRoute("/dashboard/settings")({ component: Settings });

function Settings() {
  const user = getUser();
  return (
    <FactoryPageShell title="Settings">
      {(factory) => (
        <div className="space-y-6">
          {user?.role === "factory_owner" && (
            <FactoryOnboarding onCreated={() => window.location.reload()} />
          )}
          {user?.role === "factory_owner" ? (
            <FactoryProfileForm factory={factory} onUpdated={() => undefined} />
          ) : (
            <section className="rounded-2xl border border-border bg-surface p-6 shadow-sm">
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-primary">Factory access</p>
              <h2 className="mt-2 text-xl font-semibold text-primary">{factory.name}</h2>
              <p className="mt-2 text-sm text-muted-foreground">Your manager access is limited to this assigned factory.</p>
            </section>
          )}
        </div>
      )}
    </FactoryPageShell>
  );
}
