from recommendation_engine.main import (
    run_recommendation_engine
)


EMISSIONS = {
    "electricity": 35000,
    "diesel": 10000,
    "raw_material": 3000,
    "waste": 500,
    "transport": 1000
}


RANKED_SOURCES = [
    {
        "source": "electricity",
        "emission": 35000
    },
    {
        "source": "diesel",
        "emission": 10000
    },
    {
        "source": "raw_material",
        "emission": 3000
    },
    {
        "source": "transport",
        "emission": 1000
    },
    {
        "source": "waste",
        "emission": 500
    }
]


def test_recommendation_engine_returns_results():

    recommendations = run_recommendation_engine(
        EMISSIONS,
        RANKED_SOURCES
    )

    assert isinstance(recommendations, list)
    assert len(recommendations) > 0


def test_maximum_three_recommendations():

    recommendations = run_recommendation_engine(
        EMISSIONS,
        RANKED_SOURCES
    )

    assert len(recommendations) <= 3


def test_recommendation_required_fields():

    recommendations = run_recommendation_engine(
        EMISSIONS,
        RANKED_SOURCES
    )

    required_fields = [
        "id",
        "name",
        "source",
        "predicted_co2_reduction",
        "cost",
        "savings",
        "roi",
        "feasibility",
        "score"
    ]

    for recommendation in recommendations:

        for field in required_fields:

            assert field in recommendation, (
                f"Missing field: {field}"
            )


def test_recommendation_scores_valid():

    recommendations = run_recommendation_engine(
        EMISSIONS,
        RANKED_SOURCES
    )

    for recommendation in recommendations:

        score = recommendation["score"]

        assert 0 <= score <= 1


def test_roi_valid():

    recommendations = run_recommendation_engine(
        EMISSIONS,
        RANKED_SOURCES
    )

    for recommendation in recommendations:

        expected_roi = (
            recommendation["savings"]
            / recommendation["cost"]
        )

        assert abs(
            recommendation["roi"]
            - expected_roi
        ) < 0.000001


def test_ranked_highest_source():

    assert RANKED_SOURCES[0]["source"] == "electricity"

    assert (
        RANKED_SOURCES[0]["emission"]
        == max(EMISSIONS.values())
    )


def test_empty_ranked_sources():

    recommendations = run_recommendation_engine(
        {},
        []
    )

    assert recommendations == []