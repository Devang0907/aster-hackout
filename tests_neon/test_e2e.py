from .conftest import (
    FACTORY_ID,
    EXPECTED_TOTAL_CO2E,
)


def test_complete_neon_ml_flow(
    client,
    calculated_payload,
):
    # 1. Confirm factory exists through the collection API.
    response = client.get("/api/factories/")
    assert response.status_code == 200, response.text

    factories = response.json()

    assert any(
        str(factory.get("id")) == FACTORY_ID
        for factory in factories
    )

    # 2. Emissions calculation ran and returned Neon-backed values.
    payload = calculated_payload

    carbon_result = payload[
        "emissions"
    ]["carbon_result"]

    assert float(
        carbon_result["total_co2e"]
    ) == EXPECTED_TOTAL_CO2E

    sources = payload[
        "emissions"
    ]["emission_sources"]

    assert sources[0]["source_type"] == "transport"

    # 3. ML engine ran.
    ml = payload[
        "recommendations"
    ]["ml_recommendations"]

    assert 0 < len(ml) <= 3

    assert all(
        recommendation[
            "predicted_co2_reduction"
        ] >= 0
        for recommendation in ml
    )

    # 4. Recommendations can be read back from Neon.
    response = client.get(
        f"/api/recommendations/{FACTORY_ID}"
    )

    assert response.status_code == 200, response.text

    saved = response.json()[
        "recommendations"
    ]

    assert len(saved) > 0

    # At least one DB recommendation must contain ML-populated values.
    assert any(
        float(
            recommendation.get(
                "estimated_co2_reduction"
            ) or 0
        ) > 0
        and
        float(
            recommendation.get(
                "estimated_annual_savings"
            ) or 0
        ) > 0
        for recommendation in saved
    )
