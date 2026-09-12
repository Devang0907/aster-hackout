import { createFileRoute } from "@tanstack/react-router";
import { RecommendationList } from "@/components/dashboard/RecommendationList";
import { FactoryPageShell } from "@/components/dashboard/FactoryPageShell";

export const Route = createFileRoute("/dashboard/recommendations")({ component: Recommendations });

function Recommendations() {
  return (
    <FactoryPageShell title="Recommendations">
      {(factory) => <RecommendationList factoryId={factory.id} />}
    </FactoryPageShell>
  );
}
