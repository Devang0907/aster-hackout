import pytest
from recommendation_engine.services.recommendation_engine import generate_recommendations


def test_engine_generates_recommendations_with_supplied_model_artifact() -> None:
    recommendations = generate_recommendations(
        {
            "electricity": 1_000,
            "diesel": 500,
            "raw_material": 300,
            "waste": 100,
            "transport": 50,
        },
        [
            {"source": "electricity", "emission": 1_000},
            {"source": "material_co2e", "emission": 300},
        ],
    )

    assert recommendations
    assert recommendations[0]["predicted_co2_reduction"] >= 0
    assert len(recommendations) <= 3


def test_engine_accepts_backend_source_names() -> None:
    recommendations = generate_recommendations(
        {"electricity": 1_000, "diesel": 0, "raw_material": 0, "waste": 0, "transport": 0},
        [{"sourceType": "electricity_co2e", "emissionsCo2e": 1_000}],
    )

    assert recommendations
    assert all(item["source"] == "electricity" for item in recommendations)


def test_engine_reproduces_fullbackend_demo_output() -> None:
    emissions = {
        "electricity": 35_000,
        "diesel": 0,
        "raw_material": 92_500,
        "waste": 500,
        "transport": 255_000,
    }
    recommendations = generate_recommendations(
        emissions,
        [
            {"source": "transport", "emission": 255_000},
            {"source": "raw_material", "emission": 92_500},
            {"source": "electricity", "emission": 35_000},
            {"source": "waste", "emission": 500},
        ],
    )

    assert [item["id"] for item in recommendations] == [
        "electric_transport",
        "transport_optimization",
        "recycled_material",
    ]
    assert recommendations[0]["predicted_co2_reduction"] == pytest.approx(68_484.248333)
    assert recommendations[1]["predicted_co2_reduction"] == pytest.approx(26_434.535194)
    assert recommendations[2]["predicted_co2_reduction"] == pytest.approx(16_944.588731)
    assert [item["score"] for item in recommendations] == pytest.approx(
        [0.62, 0.5215548624, 0.5187225103]
    )
