import httpx


JSON_SERVER = "http://localhost:3000"

FASTAPI = "http://localhost:8000"

FACTORY_ID = (
    "33333333-3333-3333-3333-333333333333"
)


def test_complete_recommendation_flow():

    # ----------------------------------
    # 1. Make sure factory exists
    # ----------------------------------

    factory_response = httpx.get(
        f"{JSON_SERVER}/factories/{FACTORY_ID}"
    )

    assert factory_response.status_code == 200


    # ----------------------------------
    # 2. Verify input carbon data
    # ----------------------------------

    carbon_response = httpx.get(
        f"{JSON_SERVER}/carbon_results"
    )

    assert carbon_response.status_code == 200

    carbon_results = carbon_response.json()

    factory_carbon = [
        result
        for result in carbon_results
        if str(result.get("factory_id"))
        == FACTORY_ID
    ]

    assert len(factory_carbon) >= 5


    # ----------------------------------
    # 3. Call FastAPI
    # ----------------------------------

    response = httpx.get(
        f"{FASTAPI}/api/recommendations/{FACTORY_ID}",
        timeout=30
    )

    assert response.status_code == 200

    result = response.json()


    # ----------------------------------
    # 4. Verify engine output
    # ----------------------------------

    recommendations = result[
        "recommendations"
    ]

    assert len(recommendations) > 0
    assert len(recommendations) <= 3


    # ----------------------------------
    # 5. Verify correct emissions
    # ----------------------------------

    emissions = result["emissions"]

    assert emissions["electricity"] == 35000
    assert emissions["diesel"] == 10000
    assert emissions["raw_material"] == 3000
    assert emissions["waste"] == 500
    assert emissions["transport"] == 1000


    # ----------------------------------
    # 6. Verify ranking
    # ----------------------------------

    ranked = result["ranked_sources"]

    assert ranked[0]["source"] == "electricity"
    assert ranked[0]["emission"] == 35000


    # ----------------------------------
    # 7. Verify recommendation fields
    # ----------------------------------

    for recommendation in recommendations:

        assert "name" in recommendation
        assert "source" in recommendation

        assert (
            "predicted_co2_reduction"
            in recommendation
        )

        assert "cost" in recommendation
        assert "savings" in recommendation
        assert "roi" in recommendation
        assert "feasibility" in recommendation
        assert "score" in recommendation


    # ----------------------------------
    # 8. Verify saved in JSON Server
    # ----------------------------------

    saved_response = httpx.get(
        f"{JSON_SERVER}/recommendations"
    )

    assert saved_response.status_code == 200

    saved = saved_response.json()

    factory_saved = [
        recommendation
        for recommendation in saved
        if str(
            recommendation.get("factory_id")
        ) == FACTORY_ID
    ]

    assert len(factory_saved) > 0