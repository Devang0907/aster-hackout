import { useEffect, useState } from "react";
import { post, get } from "@/lib/api";

interface EmissionsAnalysisFormProps {
  factoryId: string;
  onComplete: () => void;
}

interface Material {
  id: string;
  name: string;
  materialType: string;
}

const inputClass =
  "w-full rounded-lg border border-border bg-background px-3 py-2.5 text-sm text-primary focus:outline-none focus:ring-2 focus:ring-primary/40";

function currentMonthStart() {
  const date = new Date();
  return new Date(date.getFullYear(), date.getMonth(), 1).toISOString().slice(0, 10);
}

function currentMonthEnd() {
  const date = new Date();
  return new Date(date.getFullYear(), date.getMonth() + 1, 0).toISOString().slice(0, 10);
}

export function EmissionsAnalysisForm({ factoryId, onComplete }: EmissionsAnalysisFormProps) {
  const [materials, setMaterials] = useState<Material[]>([]);
  const [periodStart, setPeriodStart] = useState(currentMonthStart);
  const [periodEnd, setPeriodEnd] = useState(currentMonthEnd);
  const [materialId, setMaterialId] = useState("");
  const [energy, setEnergy] = useState({
    energyType: "grid electricity",
    quantity: "",
    unit: "kWh",
    renewablePercentage: "0",
  });
  const [material, setMaterial] = useState({ quantity: "", unit: "kg", recycledPercentage: "0" });
  const [waste, setWaste] = useState({
    wasteType: "general waste",
    quantity: "",
    unit: "kg",
    recycledQuantity: "0",
    recoveredQuantity: "0",
    disposedQuantity: "0",
  });
  const [logistics, setLogistics] = useState({
    transportType: "raw materials",
    mode: "road",
    distanceKm: "",
    weightTonnes: "",
    trips: "1",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    get("/api/v1/catalogs/materials")
      .then(async (response) => {
        if (!response.ok) throw new Error("Unable to load materials");
        const data = await response.json();
        setMaterials(data);
        if (data[0]) setMaterialId(data[0].id);
      })
      .catch((err) => setError(err instanceof Error ? err.message : "Unable to load materials"));
  }, []);

  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    setError("");
    setLoading(true);

    try {
      if (!materialId) throw new Error("Add at least one catalog material before calculating");
      if (
        !energy.quantity ||
        !material.quantity ||
        !waste.quantity ||
        !logistics.distanceKm ||
        !logistics.weightTonnes
      ) {
        throw new Error("Complete every activity section so emissions can be calculated");
      }

      const periodResponse = await post(`/api/v1/factories/${factoryId}/reporting-periods`, {
        periodStart,
        periodEnd,
      });
      const period = await periodResponse.json();
      if (!periodResponse.ok) throw new Error(period.detail || "Unable to create reporting period");

      const periodId = period.id;
      const records = [
        post(`/api/v1/factories/${factoryId}/energy-usage`, {
          reportingPeriodId: periodId,
          energyType: energy.energyType,
          quantity: Number(energy.quantity),
          unit: energy.unit,
          renewablePercentage: Number(energy.renewablePercentage),
        }),
        post(`/api/v1/factories/${factoryId}/material-usage`, {
          reportingPeriodId: periodId,
          materialId,
          quantity: Number(material.quantity),
          unit: material.unit,
          recycledPercentage: Number(material.recycledPercentage),
        }),
        post(`/api/v1/factories/${factoryId}/waste-streams`, {
          reportingPeriodId: periodId,
          wasteType: waste.wasteType,
          quantity: Number(waste.quantity),
          unit: waste.unit,
          recycledQuantity: Number(waste.recycledQuantity),
          recoveredQuantity: Number(waste.recoveredQuantity),
          disposedQuantity: Number(waste.disposedQuantity),
        }),
        post(`/api/v1/factories/${factoryId}/logistics`, {
          reportingPeriodId: periodId,
          transportType: logistics.transportType,
          mode: logistics.mode,
          distanceKm: Number(logistics.distanceKm),
          weightTonnes: Number(logistics.weightTonnes),
          trips: Number(logistics.trips),
        }),
      ];
      const responses = await Promise.all(records);
      for (const response of responses) {
        if (!response.ok) {
          const data = await response.json();
          throw new Error(data.detail || "Unable to save emissions activity");
        }
      }

      const submitResponse = await post(
        `/api/v1/factories/${factoryId}/reporting-periods/${periodId}/submit`,
        {},
      );
      const result = await submitResponse.json();
      if (!submitResponse.ok) throw new Error(result.detail || "Unable to calculate emissions");
      onComplete();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to calculate emissions");
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="rounded-2xl border border-border bg-surface p-6 shadow-sm sm:p-8">
      <div className="mb-7">
        <p className="text-xs font-semibold uppercase tracking-[0.18em] text-primary">
          New analysis
        </p>
        <h2 className="mt-2 text-2xl font-semibold text-primary">
          Calculate your factory footprint
        </h2>
        <p className="mt-2 text-sm leading-6 text-muted-foreground">
          Enter one reporting period. CarbonLoop will calculate emissions, identify leak points, and
          generate recommendations from the completed data.
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
            Period start *
            <input
              className={`${inputClass} mt-2`}
              type="date"
              value={periodStart}
              onChange={(e) => setPeriodStart(e.target.value)}
              required
            />
          </label>
          <label className="text-sm font-medium text-secondary">
            Period end *
            <input
              className={`${inputClass} mt-2`}
              type="date"
              value={periodEnd}
              onChange={(e) => setPeriodEnd(e.target.value)}
              required
            />
          </label>
        </div>

        <div className="grid gap-5 border-t border-border pt-6 sm:grid-cols-2">
          <div className="sm:col-span-2">
            <h3 className="font-semibold text-primary">Energy use</h3>
            <p className="mt-1 text-xs text-muted-foreground">
              Electricity, fuel, or other purchased energy.
            </p>
          </div>
          <label className="text-sm font-medium text-secondary">
            Energy type
            <input
              className={`${inputClass} mt-2`}
              value={energy.energyType}
              onChange={(e) => setEnergy({ ...energy, energyType: e.target.value })}
              required
            />
          </label>
          <label className="text-sm font-medium text-secondary">
            Quantity
            <input
              className={`${inputClass} mt-2`}
              type="number"
              min="0"
              step="any"
              value={energy.quantity}
              onChange={(e) => setEnergy({ ...energy, quantity: e.target.value })}
              required
            />
          </label>
          <label className="text-sm font-medium text-secondary">
            Unit
            <input
              className={`${inputClass} mt-2`}
              value={energy.unit}
              onChange={(e) => setEnergy({ ...energy, unit: e.target.value })}
              required
            />
          </label>
          <label className="text-sm font-medium text-secondary">
            Renewable share (%)
            <input
              className={`${inputClass} mt-2`}
              type="number"
              min="0"
              max="100"
              value={energy.renewablePercentage}
              onChange={(e) => setEnergy({ ...energy, renewablePercentage: e.target.value })}
            />
          </label>
        </div>

        <div className="grid gap-5 border-t border-border pt-6 sm:grid-cols-2">
          <div className="sm:col-span-2">
            <h3 className="font-semibold text-primary">Raw materials</h3>
            <p className="mt-1 text-xs text-muted-foreground">
              Choose a catalog material used during this period.
            </p>
          </div>
          <label className="text-sm font-medium text-secondary sm:col-span-2">
            Material *
            <select
              className={`${inputClass} mt-2`}
              value={materialId}
              onChange={(e) => setMaterialId(e.target.value)}
              required
            >
              <option value="">Select a material</option>
              {materials.map((item) => (
                <option key={item.id} value={item.id}>
                  {item.name} · {item.materialType}
                </option>
              ))}
            </select>
          </label>
          <label className="text-sm font-medium text-secondary">
            Quantity
            <input
              className={`${inputClass} mt-2`}
              type="number"
              min="0"
              step="any"
              value={material.quantity}
              onChange={(e) => setMaterial({ ...material, quantity: e.target.value })}
              required
            />
          </label>
          <label className="text-sm font-medium text-secondary">
            Unit
            <input
              className={`${inputClass} mt-2`}
              value={material.unit}
              onChange={(e) => setMaterial({ ...material, unit: e.target.value })}
              required
            />
          </label>
          <label className="text-sm font-medium text-secondary">
            Recycled share (%)
            <input
              className={`${inputClass} mt-2`}
              type="number"
              min="0"
              max="100"
              value={material.recycledPercentage}
              onChange={(e) => setMaterial({ ...material, recycledPercentage: e.target.value })}
            />
          </label>
        </div>

        <div className="grid gap-5 border-t border-border pt-6 sm:grid-cols-2">
          <div className="sm:col-span-2">
            <h3 className="font-semibold text-primary">Waste</h3>
            <p className="mt-1 text-xs text-muted-foreground">
              Record the total waste and how it was handled.
            </p>
          </div>
          <label className="text-sm font-medium text-secondary">
            Waste type
            <input
              className={`${inputClass} mt-2`}
              value={waste.wasteType}
              onChange={(e) => setWaste({ ...waste, wasteType: e.target.value })}
              required
            />
          </label>
          <label className="text-sm font-medium text-secondary">
            Total quantity
            <input
              className={`${inputClass} mt-2`}
              type="number"
              min="0"
              step="any"
              value={waste.quantity}
              onChange={(e) => setWaste({ ...waste, quantity: e.target.value })}
              required
            />
          </label>
          <label className="text-sm font-medium text-secondary">
            Unit
            <input
              className={`${inputClass} mt-2`}
              value={waste.unit}
              onChange={(e) => setWaste({ ...waste, unit: e.target.value })}
              required
            />
          </label>
          <label className="text-sm font-medium text-secondary">
            Recycled quantity
            <input
              className={`${inputClass} mt-2`}
              type="number"
              min="0"
              step="any"
              value={waste.recycledQuantity}
              onChange={(e) => setWaste({ ...waste, recycledQuantity: e.target.value })}
            />
          </label>
          <label className="text-sm font-medium text-secondary">
            Recovered quantity
            <input
              className={`${inputClass} mt-2`}
              type="number"
              min="0"
              step="any"
              value={waste.recoveredQuantity}
              onChange={(e) => setWaste({ ...waste, recoveredQuantity: e.target.value })}
            />
          </label>
          <label className="text-sm font-medium text-secondary">
            Disposed quantity
            <input
              className={`${inputClass} mt-2`}
              type="number"
              min="0"
              step="any"
              value={waste.disposedQuantity}
              onChange={(e) => setWaste({ ...waste, disposedQuantity: e.target.value })}
            />
          </label>
        </div>

        <div className="grid gap-5 border-t border-border pt-6 sm:grid-cols-2">
          <div className="sm:col-span-2">
            <h3 className="font-semibold text-primary">Logistics</h3>
            <p className="mt-1 text-xs text-muted-foreground">
              Capture incoming or outgoing transport activity.
            </p>
          </div>
          <label className="text-sm font-medium text-secondary">
            Transport type
            <input
              className={`${inputClass} mt-2`}
              value={logistics.transportType}
              onChange={(e) => setLogistics({ ...logistics, transportType: e.target.value })}
              required
            />
          </label>
          <label className="text-sm font-medium text-secondary">
            Mode
            <input
              className={`${inputClass} mt-2`}
              value={logistics.mode}
              onChange={(e) => setLogistics({ ...logistics, mode: e.target.value })}
              required
            />
          </label>
          <label className="text-sm font-medium text-secondary">
            Distance (km)
            <input
              className={`${inputClass} mt-2`}
              type="number"
              min="0"
              step="any"
              value={logistics.distanceKm}
              onChange={(e) => setLogistics({ ...logistics, distanceKm: e.target.value })}
              required
            />
          </label>
          <label className="text-sm font-medium text-secondary">
            Weight (tonnes)
            <input
              className={`${inputClass} mt-2`}
              type="number"
              min="0"
              step="any"
              value={logistics.weightTonnes}
              onChange={(e) => setLogistics({ ...logistics, weightTonnes: e.target.value })}
              required
            />
          </label>
          <label className="text-sm font-medium text-secondary">
            Trips
            <input
              className={`${inputClass} mt-2`}
              type="number"
              min="0"
              step="1"
              value={logistics.trips}
              onChange={(e) => setLogistics({ ...logistics, trips: e.target.value })}
              required
            />
          </label>
        </div>

        <button
          type="submit"
          disabled={loading || materials.length === 0}
          className="rounded-full bg-primary px-6 py-3 text-sm font-semibold uppercase tracking-[0.14em] text-primary-foreground transition-opacity hover:opacity-90 disabled:opacity-50"
        >
          {loading ? "Calculating footprint..." : "Calculate and get recommendations"}
        </button>
      </form>
    </section>
  );
}
