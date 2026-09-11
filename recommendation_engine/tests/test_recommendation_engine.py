from recommendation_engine.services.recommendation_engine import (
    generate_recommendations,
)


def test_engine_generates_recommendations_without_model_artifact() -> None:
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
