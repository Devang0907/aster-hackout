import re
from datetime import date
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.schemas.carbon import CarbonResultCreate, ReportingPeriodCreate
from app.schemas.common import AuditLogCreate
from app.schemas.energy import EnergyUsageCreate
from app.schemas.material import MaterialAlternativeCreate, MaterialUsageCreate
from app.schemas.recommendation import RecommendationCreate
from app.schemas.simulation import SimulationCreate
from app.schemas.user import UserCreate, UserRole
from app.schemas.waste import WasteStreamCreate
from app.services.operational import delete_historical_result

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = (ROOT / "prisma" / "schema.prisma").read_text(encoding="utf-8")
MIGRATION = (
    ROOT / "prisma" / "migrations" / "20260911000000_initial" / "migration.sql"
).read_text(encoding="utf-8")


def test_all_eighteen_models_are_present() -> None:
    expected = {
        "User",
        "Factory",
        "ReportingPeriod",
        "Material",
        "MaterialAlternative",
        "FactoryMaterialUsage",
        "EnergyUsage",
        "WasteStream",
        "Logistics",
        "EmissionFactor",
        "CarbonResult",
        "EmissionSource",
        "Intervention",
        "Recommendation",
        "Simulation",
        "MlPipelineRun",
        "CarbonCreditResult",
        "AuditLog",
    }
    actual = set(re.findall(r"^model\s+(\w+)\s+\{", SCHEMA, flags=re.MULTILINE))
    assert actual == expected


def test_admin_role_can_be_created() -> None:
    user = UserCreate(
        id=uuid4(), fullName="Platform Admin", email="ADMIN@example.com", role="admin"
    )
    assert user.role == UserRole.admin
    assert str(user.email) == "admin@example.com"


def test_factory_manager_cannot_manage_multiple_factories() -> None:
    assert 'CONSTRAINT "factories_manager_id_key" UNIQUE ("manager_id")' in MIGRATION
    assert '@unique(map: "factories_manager_id_key")' in SCHEMA


def test_factory_has_only_one_manager_field() -> None:
    factory_block = re.search(r"model Factory \{(?P<body>.*?)\n\}", SCHEMA, re.DOTALL)
    assert factory_block is not None
    assert re.search(r"\bmanagerId\s+String\?", factory_block.group("body"))
    assert "managerIds" not in factory_block.group("body")


def test_reporting_periods_belong_to_a_factory() -> None:
    assert 'FOREIGN KEY ("factory_id") REFERENCES "factories"("id")' in MIGRATION
    with pytest.raises(ValidationError):
        ReportingPeriodCreate(periodStart=date(2026, 2, 1), periodEnd=date(2026, 1, 1))


def test_material_usage_references_valid_material_records() -> None:
    assert (
        'FOREIGN KEY ("material_id") REFERENCES "materials"("id") ON DELETE RESTRICT'
        in MIGRATION
    )
    value = MaterialUsageCreate(
        reportingPeriodId=uuid4(), materialId=uuid4(), quantity=1, unit="kg"
    )
    assert value.materialId


def test_invalid_percentages_are_rejected() -> None:
    with pytest.raises(ValidationError):
        EnergyUsageCreate(
            reportingPeriodId=uuid4(),
            energyType="solar",
            quantity=1,
            unit="kWh",
            renewablePercentage=Decimal("100.01"),
        )


def test_negative_quantities_are_rejected() -> None:
    with pytest.raises(ValidationError):
        MaterialUsageCreate(
            reportingPeriodId=uuid4(), materialId=uuid4(), quantity=-1, unit="kg"
        )


def test_material_cannot_use_itself_as_an_alternative() -> None:
    material_id = uuid4()
    with pytest.raises(ValidationError):
        MaterialAlternativeCreate(
            materialId=material_id, alternativeMaterialId=material_id
        )


def test_duplicate_material_alternatives_are_prevented() -> None:
    assert (
        'CONSTRAINT "material_alternatives_pair_key" UNIQUE '
        '("material_id", "alternative_material_id")' in MIGRATION
    )


def test_carbon_results_reference_reporting_periods() -> None:
    assert (
        'ALTER TABLE "carbon_results" ADD CONSTRAINT "carbon_results_period_id_fkey"'
        in MIGRATION
    )
    result = CarbonResultCreate(
        reportingPeriodId=uuid4(),
        totalCo2e=10,
        netCo2e=9,
        calculationVersion="calc-v1",
    )
    assert result.reportingPeriodId
    assert 'CONSTRAINT "carbon_results_pipeline_run_id_key" UNIQUE' in MIGRATION
    assert 'CREATE FUNCTION "check_carbon_result_pipeline_trace"' in MIGRATION


def test_recommendations_reference_interventions() -> None:
    assert (
        'FOREIGN KEY ("intervention_id") REFERENCES "interventions"("id")'
        in MIGRATION
    )
    recommendation = RecommendationCreate(
        resultId=uuid4(), interventionId=uuid4(), priority=1
    )
    assert recommendation.interventionId


def test_simulations_preserve_json_assumptions() -> None:
    assumptions = {"renewable_electricity": 35, "nested": {"enabled": True}}
    simulation = SimulationCreate(
        baseResultId=uuid4(),
        name="Scenario A",
        assumptions=assumptions,
        baselineCo2e=100,
        resultingCo2e=65,
        co2Reduction=35,
        co2ReductionPercentage=35,
    )
    assert simulation.assumptions == assumptions
    assert '"assumptions" JSONB NOT NULL' in MIGRATION


def test_simulation_reduction_values_must_be_consistent() -> None:
    with pytest.raises(ValidationError):
        SimulationCreate(
            baseResultId=uuid4(),
            name="Inconsistent scenario",
            assumptions={},
            baselineCo2e=100,
            resultingCo2e=65,
            co2Reduction=20,
            co2ReductionPercentage=20,
        )


def test_zero_baseline_requires_zero_reduction_values() -> None:
    with pytest.raises(ValidationError):
        SimulationCreate(
            baseResultId=uuid4(),
            name="Invalid zero baseline",
            assumptions={},
            baselineCo2e=0,
            resultingCo2e=0,
            co2Reduction=0,
            co2ReductionPercentage=1,
        )


def test_audit_log_records_can_be_created() -> None:
    log = AuditLogCreate(action="FACTORY_CREATED", entityType="Factory", metadata={"x": 1})
    assert log.action == "FACTORY_CREATED"
    assert 'CREATE TABLE "audit_logs"' in MIGRATION
    assert 'CREATE TRIGGER "audit_logs_no_update"' in MIGRATION


def test_waste_allocations_cannot_exceed_total() -> None:
    with pytest.raises(ValidationError):
        WasteStreamCreate(
            reportingPeriodId=uuid4(),
            wasteType="offcuts",
            quantity=10,
            unit="kg",
            recycledQuantity=8,
            disposedQuantity=3,
        )


@pytest.mark.asyncio
async def test_historical_results_are_not_accidentally_deleted() -> None:
    from app.services.errors import ImmutableHistoryError

    with pytest.raises(ImmutableHistoryError):
        await delete_historical_result(uuid4())
    assert 'CREATE TRIGGER "carbon_results_no_delete"' in MIGRATION
    assert 'CREATE TRIGGER "emission_factors_no_update"' in MIGRATION
    assert 'CREATE TRIGGER "recommendations_no_delete"' in MIGRATION
    assert 'CREATE TRIGGER "ml_pipeline_runs_no_delete"' in MIGRATION
