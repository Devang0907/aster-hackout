import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { FactoryPageShell } from "@/components/dashboard/FactoryPageShell";
import { EmissionsAnalysisForm } from "@/components/dashboard/EmissionsAnalysisForm";
import { RecentActivity } from "@/components/dashboard/RecentActivity";

export const Route = createFileRoute("/dashboard/emissions")({ component: Emissions });

function Emissions() {
  const [version, setVersion] = useState(0);
  return (
    <FactoryPageShell title="Emissions">
      {(factory) => (
        <div className="space-y-6">
          <EmissionsAnalysisForm
            factoryId={factory.id}
            onComplete={() => setVersion((value) => value + 1)}
          />
          <RecentActivity key={version} factoryId={factory.id} />
        </div>
      )}
    </FactoryPageShell>
  );
}
