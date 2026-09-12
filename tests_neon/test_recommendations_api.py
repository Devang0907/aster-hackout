from .conftest import (
    FACTORY_ID,
    EXPECTED_EMISSIONS,
)


def test_generate_ml_recommendations(
    calculated_payload
):
    payload = calculated_payload[
        "recommendations"
    ]

    assert "ml_recommendations" in payload

    recommendations = payload[
        "ml_recommendations"
    ]

    assert 0 < len(recommendations) <= 3

    for recommendation in recommendations:
        assert recommendation[
            "predicted_co2_reduction"
        ] >= 0

        assert recommendation["cost"] > 0
        assert recommendation["savings"] >= 0

        assert (
            0
            <= recommendation["feasibility"]
            <= 1
        )

        assert (
            0
            <= recommendation["score"]
            <= 1
        )


def test_get_saved_recommendations(client):
    response = client.get(
        f"/api/recommendations/{FACTORY_ID}"
    )

    assert response.status_code == 200, response.text

    data = response.json()

    assert str(
        data["factory"]["id"]
    ) == FACTORY_ID

    emissions = data["emissions"]

    for key, expected in EXPECTED_EMISSIONS.items():
        assert float(emissions[key]) == expected

    assert isinstance(
        data["ranked_sources"],
        list,
    )

    assert isinstance(
        data["recommendations"],
        list,
    )

    assert len(
        data["recommendations"]
    ) > 0
