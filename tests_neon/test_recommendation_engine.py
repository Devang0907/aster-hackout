from recommendation_engine.main import run_recommendation_engine


EMISSIONS = {
    "electricity": 35000.0,
    "diesel": 0.0,
    "raw_material": 92500.0,
    "waste": 500.0,
    "transport": 255000.0,
}

RANKED_SOURCES = [
    {"source": "transport", "emission": 255000.0},
    {"source": "raw_material", "emission": 92500.0},
    {"source": "electricity", "emission": 35000.0},
    {"source": "waste", "emission": 500.0},
]


def get_recommendations():
    return run_recommendation_engine(
        EMISSIONS,
        RANKED_SOURCES,
    )


def test_engine_returns_results():
    recommendations = get_recommendations()

    assert isinstance(recommendations, list)
    assert 0 < len(recommendations) <= 3


def test_required_fields():
    required = {
        "id",
        "name",
        "source",
        "predicted_co2_reduction",
        "cost",
        "savings",
        "roi",
        "feasibility",
        "score",
    }

    for recommendation in get_recommendations():
        assert required.issubset(recommendation.keys())


def test_scores_are_valid():
    for recommendation in get_recommendations():
        assert 0 <= recommendation["score"] <= 1
        assert 0 <= recommendation["feasibility"] <= 1
        assert recommendation["predicted_co2_reduction"] >= 0


def test_roi_formula():
    for recommendation in get_recommendations():
        expected = (
            recommendation["savings"]
            / recommendation["cost"]
        )

        assert abs(
            recommendation["roi"] - expected
        ) < 1e-9


def test_results_sorted_by_score():
    recommendations = get_recommendations()

    scores = [
        recommendation["score"]
        for recommendation in recommendations
    ]

    assert scores == sorted(
        scores,
        reverse=True,
    )


def test_zero_sources_return_empty():
    assert run_recommendation_engine({}, []) == []
