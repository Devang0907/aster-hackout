import sys
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

from app.schemas.carbon import CarbonResultCreate, EmissionSourceCreate, MlPipelineRunCreate
from app.schemas.recommendation import RecommendationCreate
from app.services.calculations import (
    _period,
    complete_pipeline_run,
    create_pipeline_run,
    update_pipeline_run,
)
from app.services.errors import ConflictError

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from recommendation_engine.data.interventions import INTERVENTIONS  # noqa: E402
from recommendation_engine.services.recommendation_engine import (  # noqa: E402
    generate_recommendations,
)

ZERO = Decimal("0")
CALCULATION_VERSION = "1.0"
MODEL_VERSION = "fullbackend-random-forest-1.0"
SOURCE_METADATA = {
    "electricity": {"type": "energy", "name": "Electricity"},
    "diesel": {"type": "fuel", "name": "Fuel"},
    "raw_material": {"type": "material", "name": "Raw Material"},
    "transport": {"type": "transport", "name": "Transport"},
    "waste": {"type": "waste", "name": "Waste"},
}
SOURCE_ALIASES = {
    "solar installation": "renewable_electricity",
    "energy efficiency": "energy_efficiency",
    "recycled material substitution": "recycled_material",
    "waste recovery": "waste_recovery",
    "electrification": "fuel_switching",
    "process optimization": "material_efficiency",
    "water recycling": "waste_recovery",
    "material reuse": "material_efficiency",
    "packaging reduction": "material_efficiency",
}


def _decimal(value: Any) -> Decimal:
    return ZERO if value is None else Decimal(str(value))


def _factor_value(factors: list[Any], category: str, keywords: list[str]) -> Decimal:
    category = category.lower()
    category_factors = [
        factor
        for factor in factors
        if str(factor.category).lower() == category
    ]
    normalized_keywords = [keyword.strip().lower() for keyword in keywords if keyword.strip()]
    exact = [
        factor
        for factor in category_factors
        if str(factor.activity).strip().lower() in normalized_keywords
    ]
    if exact:
        return _decimal(exact[0].factor)
    matching = [
        factor
        for factor in category_factors
        if any(keyword in str(factor.activity).lower() for keyword in normalized_keywords)
    ]
    if not matching:
        matching = category_factors
    return _decimal(matching[0].factor) if matching else ZERO


def _severity(percentage: Decimal) -> str:
    if percentage >= 50:
        return "critical"
    if percentage >= 20:
        return "high"
    if percentage >= 5:
        return "medium"
    return "low"


def _ranked_sources(emissions: dict[str, Decimal]) -> list[dict[str, Any]]:
    total = sum(emissions.values(), ZERO)
    ranked = sorted(emissions.items(), key=lambda item: item[1], reverse=True)
    return [
        {
            "source": source,
            "emission": float(amount),
            "percentage": float((amount / total * 100) if total else ZERO),
        }
        for source, amount in ranked
        if amount > ZERO
    ]


async def _load_period_data(factory_id: UUID, period_id: UUID, database: Any) -> dict[str, Any]:
    await _period(factory_id, period_id, database)
    factory = await database.factory.find_unique(where={"id": str(factory_id)})
    filters = {"factoryId": str(factory_id), "reportingPeriodId": str(period_id)}
    material_usage = await database.factorymaterialusage.find_many(
        where=filters, include={"material": True}
    )
    energy_usage = await database.energyusage.find_many(where=filters)
    waste_streams = await database.wastestream.find_many(where=filters)
    logistics = await database.logistics.find_many(where=filters)
    factors = await database.emissionfactor.find_many()
    interventions = await database.intervention.find_many()
    return {
        "factory": factory,
        "material_usage": material_usage,
        "energy_usage": energy_usage,
        "waste_streams": waste_streams,
        "logistics": logistics,
        "factors": factors,
        "interventions": interventions,
    }


def _calculate_emissions(data: dict[str, Any]) -> tuple[dict[str, Decimal], Decimal]:
    factors = data["factors"]
    emissions = {
        "electricity": ZERO,
        "diesel": ZERO,
        "raw_material": ZERO,
        "waste": ZERO,
        "transport": ZERO,
    }
    # The supplied CarbonWise calculation stores the reported renewable share but
    # does not infer an offset from it. A defensible offset needs a separate,
    # evidenced renewable-generation or contractual instrument calculation.
    renewable_offset = ZERO

    for record in data["energy_usage"]:
        energy_type = str(record.energyType).lower()
        category = "fuel" if any(value in energy_type for value in ("diesel", "fuel")) else "energy"
        factor = _factor_value(factors, category, [energy_type, str(record.source or "").lower()])
        emission = _decimal(record.quantity) * factor
        target = "diesel" if category == "fuel" else "electricity"
        emissions[target] += emission

    for record in data["material_usage"]:
        material = record.material
        emissions["raw_material"] += _decimal(record.quantity) * _decimal(material.carbonFactor)

    for record in data["waste_streams"]:
        factor = _factor_value(factors, "waste", [str(record.wasteType).lower()])
        emissions["waste"] += _decimal(record.quantity) * factor

    for record in data["logistics"]:
        factor = _factor_value(
            factors,
            "transport",
            [
                f"{record.fuelType or ''} {record.transportType}".strip().lower(),
                str(record.transportType).lower(),
                str(record.mode).lower(),
            ],
        )
        activity = (
            _decimal(record.distanceKm)
            * _decimal(record.weightTonnes)
            * _decimal(record.trips)
        )
        emissions["transport"] += activity * factor

    return emissions, renewable_offset


def _engine_catalog(records: list[Any]) -> dict[str, dict[str, Any]]:
    catalog: dict[str, dict[str, Any]] = {}
    for record in records:
        intervention_type = str(getattr(record, "interventionType", "") or "").lower()
        key = intervention_type if intervention_type in INTERVENTIONS else None
        if key is None:
            key = SOURCE_ALIASES.get(str(record.name).lower())
        if key is None:
            continue
        template = dict(INTERVENTIONS[key])
        cost = record.estimatedCostMax or record.estimatedCostMin
        feasibility = _decimal(record.feasibilityScore)
        reduction = _decimal(record.expectedCo2ReductionPercentage)
        template.update(
            {
                "id": str(record.id),
                "name": record.name,
                "cost": float(cost if cost is not None else template["cost"]),
                "feasibility": float(feasibility / 100 if feasibility > 1 else feasibility)
                if feasibility
                else template["feasibility"],
                "co2_reduction_rate": float(reduction / 100 if reduction > 1 else reduction)
                if reduction
                else template["co2_reduction_rate"],
            }
        )
        catalog[str(record.id)] = template
    return catalog


def _carbon_payload(
    factory: Any,
    period_id: UUID,
    run_id: UUID,
    emissions: dict[str, Decimal],
    renewable_offset: Decimal,
) -> CarbonResultCreate:
    total = sum(emissions.values(), ZERO)
    net = max(ZERO, total - renewable_offset)
    production_capacity = _decimal(getattr(factory, "productionCapacity", None))
    carbon_intensity = net / production_capacity if production_capacity > ZERO else None
    calculated_at = datetime.now(UTC)
    return CarbonResultCreate(
        reportingPeriodId=period_id,
        pipelineRunId=run_id,
        totalCo2e=total,
        electricityCo2e=emissions["electricity"],
        fuelCo2e=emissions["diesel"],
        materialCo2e=emissions["raw_material"],
        transportCo2e=emissions["transport"],
        wasteCo2e=emissions["waste"],
        renewableOffset=renewable_offset,
        netCo2e=net,
        carbonIntensity=carbon_intensity,
        carbonIntensityUnit="kgCO2e/unit" if carbon_intensity is not None else None,
        calculationVersion=CALCULATION_VERSION,
        mlModelVersion=MODEL_VERSION,
        calculatedAt=calculated_at,
    )


async def run_reporting_period_pipeline(
    factory_id: UUID, period_id: UUID, database: Any
) -> Any:
    period = await _period(factory_id, period_id, database)
    status = str(getattr(period.status, "value", period.status))
    if status not in {"submitted", "processing"}:
        raise ConflictError("only submitted reporting periods may be processed")

    run = await create_pipeline_run(
        factory_id,
        MlPipelineRunCreate(
            reportingPeriodId=period_id,
            pipelineVersion="backend-recommendation-v1",
            modelVersion=MODEL_VERSION,
        ),
        database,
    )
    try:
        await update_pipeline_run(run.id, "running", database)
        await database.reportingperiod.update(
            where={"id": str(period_id)}, data={"status": "processing"}
        )
        data = await _load_period_data(factory_id, period_id, database)
        emissions, renewable_offset = _calculate_emissions(data)
        ranked_sources = _ranked_sources(emissions)
        catalog = _engine_catalog(data["interventions"])
        recommendations = generate_recommendations(
            {key: float(value) for key, value in emissions.items()},
            ranked_sources,
            interventions=catalog,
        )
        result_payload = _carbon_payload(
            data["factory"], period_id, run.id, emissions, renewable_offset
        )
        total = sum(emissions.values(), ZERO)
        sorted_emissions = sorted(emissions.items(), key=lambda item: item[1], reverse=True)
        source_payloads = [
            EmissionSourceCreate(
                resultId=uuid4(),
                sourceType=SOURCE_METADATA[source]["type"],
                sourceName=SOURCE_METADATA[source]["name"],
                emissionsCo2e=amount,
                percentage=(amount / total * 100) if total else ZERO,
                severity=_severity((amount / total * 100) if total else ZERO),
                rank=rank,
                explanation=(
                    f"{SOURCE_METADATA[source]['name']} contributes {amount:.2f} kgCO2e, "
                    f"which is {((amount / total * 100) if total else ZERO):.2f}% of "
                    "total emissions."
                ),
            )
            for rank, (source, amount) in enumerate(sorted_emissions, start=1)
        ]
        source_percentages = {
            source: (amount / total * 100) if total else ZERO
            for source, amount in emissions.items()
        }
        recommendation_payloads = [
            RecommendationCreate(
                resultId=uuid4(),
                interventionId=UUID(recommendation["id"]),
                priority=priority,
                recommendationScore=Decimal(str(recommendation["score"] * 100)),
                estimatedCo2Reduction=Decimal(str(recommendation["predicted_co2_reduction"])),
                estimatedCost=Decimal(str(recommendation["cost"])),
                estimatedAnnualSavings=Decimal(str(recommendation["savings"])),
                paybackMonths=(
                    Decimal(str(recommendation["cost"]))
                    / Decimal(str(recommendation["savings"]))
                    * 12
                    if recommendation["savings"]
                    else None
                ),
                feasibilityScore=Decimal(str(recommendation["feasibility"] * 100)),
                confidenceScore=Decimal("85"),
                aiExplanation=(
                    f"{SOURCE_METADATA[recommendation['source']]['name']} produces "
                    f"{emissions[recommendation['source']]:.2f} kgCO2e "
                    f"({source_percentages[recommendation['source']]:.2f}% of total emissions). "
                    f"The {MODEL_VERSION} model predicts that {recommendation['name']} "
                    f"could reduce approximately "
                    f"{recommendation['predicted_co2_reduction']:.2f} kgCO2e."
                ),
            )
            for priority, recommendation in enumerate(recommendations, start=1)
        ]
        return await complete_pipeline_run(
            factory_id,
            run.id,
            result_payload,
            source_payloads,
            recommendation_payloads,
            database,
            recommendation_source_types=[
                SOURCE_METADATA[recommendation["source"]]["type"]
                for recommendation in recommendations
            ],
        )
    except Exception as exc:
        await update_pipeline_run(run.id, "failed", database, str(exc))
        await database.reportingperiod.update(
            where={"id": str(period_id)}, data={"status": "failed"}
        )
        raise
