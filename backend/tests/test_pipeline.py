from decimal import Decimal
from types import SimpleNamespace
from uuid import uuid4

from app.services.pipeline import (
    _calculate_emissions,
    _engine_catalog,
    _ranked_sources,
    _severity,
)


def test_pipeline_calculates_backend_operational_categories() -> None:
    emissions, renewable_offset = _calculate_emissions(
        {
            "factors": [
                SimpleNamespace(
                    category="energy", activity="grid electricity", factor=Decimal("2")
                ),
                SimpleNamespace(
                    category="transport", activity="road freight", factor=Decimal("3")
                ),
            ],
            "energy_usage": [
                SimpleNamespace(
                    energyType="electricity",
                    source="grid",
                    quantity=Decimal("10"),
                    renewablePercentage=Decimal("25"),
                )
            ],
            "material_usage": [],
            "waste_streams": [],
            "logistics": [
                SimpleNamespace(
                    mode="road",
                    transportType="freight",
                    distanceKm=Decimal("5"),
                    weightTonnes=Decimal("2"),
                    trips=2,
                )
            ],
        }
    )

    assert emissions["electricity"] == Decimal("20")
    assert emissions["transport"] == Decimal("60")
    assert renewable_offset == Decimal("0")


def test_pipeline_ranks_only_nonzero_sources() -> None:
    ranked = _ranked_sources(
        {"electricity": Decimal("10"), "diesel": Decimal("0"), "waste": Decimal("5")}
    )

    assert [item["source"] for item in ranked] == ["electricity", "waste"]
    assert ranked[0]["percentage"] == 66.66666666666667


def test_pipeline_uses_database_intervention_ids() -> None:
    intervention_id = uuid4()
    catalog = _engine_catalog(
        [
            SimpleNamespace(
                id=intervention_id,
                name="Energy Efficiency",
                interventionType=None,
                estimatedCostMax=None,
                estimatedCostMin=None,
                feasibilityScore=None,
                expectedCo2ReductionPercentage=None,
            )
        ]
    )

    assert str(intervention_id) in catalog
    assert catalog[str(intervention_id)]["source"] == "electricity"


def test_pipeline_uses_stable_engine_intervention_type() -> None:
    intervention_id = uuid4()
    catalog = _engine_catalog(
        [
            SimpleNamespace(
                id=intervention_id,
                name="Database display name",
                interventionType="electric_transport",
                estimatedCostMax=Decimal("60000"),
                estimatedCostMin=Decimal("60000"),
                feasibilityScore=Decimal("60"),
                expectedCo2ReductionPercentage=Decimal("30"),
            )
        ]
    )

    assert catalog[str(intervention_id)]["source"] == "transport"
    assert catalog[str(intervention_id)]["cost"] == 60_000


def test_pipeline_reproduces_carbonwise_demo_calculation() -> None:
    emissions, renewable_offset = _calculate_emissions(
        {
            "factors": [
                SimpleNamespace(category="energy", activity="electricity", factor="0.28"),
                SimpleNamespace(category="waste", activity="industrial waste", factor="0.5"),
                SimpleNamespace(category="transport", activity="diesel truck", factor="0.1"),
            ],
            "energy_usage": [
                SimpleNamespace(
                    energyType="Electricity",
                    source="Grid",
                    quantity="125000",
                    renewablePercentage="15",
                )
            ],
            "material_usage": [
                SimpleNamespace(
                    quantity="50000",
                    material=SimpleNamespace(carbonFactor="1.85"),
                )
            ],
            "waste_streams": [
                SimpleNamespace(wasteType="Industrial Waste", quantity="1000")
            ],
            "logistics": [
                SimpleNamespace(
                    mode="road",
                    transportType="Truck",
                    fuelType="diesel",
                    distanceKm="850",
                    weightTonnes="120",
                    trips=25,
                )
            ],
        }
    )

    assert emissions == {
        "electricity": Decimal("35000.00"),
        "diesel": Decimal("0"),
        "raw_material": Decimal("92500.00"),
        "waste": Decimal("500.0"),
        "transport": Decimal("255000.0"),
    }
    assert sum(emissions.values(), Decimal("0")) == Decimal("383000.00")
    assert renewable_offset == Decimal("0")


def test_pipeline_uses_reference_severity_thresholds() -> None:
    assert _severity(Decimal("50")) == "critical"
    assert _severity(Decimal("24.15")) == "high"
    assert _severity(Decimal("9.14")) == "medium"
    assert _severity(Decimal("0.13")) == "low"
