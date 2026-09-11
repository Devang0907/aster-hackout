from decimal import Decimal
from types import SimpleNamespace
from uuid import uuid4

from app.services.pipeline import _calculate_emissions, _engine_catalog, _ranked_sources


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
    assert renewable_offset == Decimal("5")


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
                estimatedCostMax=None,
                estimatedCostMin=None,
                feasibilityScore=None,
                expectedCo2ReductionPercentage=None,
            )
        ]
    )

    assert str(intervention_id) in catalog
    assert catalog[str(intervention_id)]["source"] == "electricity"
