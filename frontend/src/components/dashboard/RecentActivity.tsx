import { useEffect, useState } from "react";
import { get } from "@/lib/api";

interface CarbonResult {
  id: string;
  netCo2e: number;
  calculatedAt: string;
  reportingPeriodId: string;
}

interface RecentActivityProps {
  factoryId: string;
}

export function RecentActivity({ factoryId }: RecentActivityProps) {
  const [results, setResults] = useState<CarbonResult[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchResults() {
      try {
        const response = await get(`/api/v1/factories/${factoryId}/carbon-results`);
        const data = await response.json();
        setResults(data.slice(0, 5)); // Show last 5 results
      } catch (error) {
        console.error("Failed to fetch carbon results:", error);
      } finally {
        setLoading(false);
      }
    }

    fetchResults();
  }, [factoryId]);

  if (loading) {
    return (
      <div className="rounded-xl border border-border bg-surface p-6">
        <h3 className="text-lg font-semibold text-primary mb-4">Latest Carbon Results</h3>
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-12 rounded-lg bg-mist animate-pulse" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="rounded-xl border border-border bg-surface p-6">
      <h3 className="text-lg font-semibold text-primary mb-4">Latest Carbon Results</h3>
      {results.length === 0 ? (
        <p className="text-sm text-muted-foreground">No carbon results available</p>
      ) : (
        <div className="space-y-3">
          {results.map((result) => (
            <div
              key={result.id}
              className="flex items-center justify-between rounded-lg border border-border bg-background p-4"
            >
              <div>
                <p className="text-sm font-medium text-primary">
                  {Number(result.netCo2e).toFixed(2)} t CO2e
                </p>
                <p className="text-xs text-muted-foreground">
                  {new Date(result.calculatedAt).toLocaleDateString()}
                </p>
              </div>
              <div className="text-xs text-muted-foreground">
                Period: {String(result.reportingPeriodId).slice(0, 8)}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
