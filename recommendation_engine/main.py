from .services.recommendation_engine import (
    generate_recommendations
)


def run_recommendation_engine(
    emissions,
    ranked_sources
):
    """
    Main entry point for the recommendation engine.

    FastAPI can call this function.
    """

    return generate_recommendations(
        emissions,
        ranked_sources
    )


if __name__ == "__main__":

    emissions = {
        "electricity": 35000,
        "diesel": 10000,
        "raw_material": 3000,
        "waste": 500,
        "transport": 1000
    }

    ranked_sources = [
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

    recommendations = run_recommendation_engine(
        emissions,
        ranked_sources
    )

    print("\n===== RECOMMENDATIONS =====\n")

    for i, recommendation in enumerate(
        recommendations,
        start=1
    ):

        print(
            f"Recommendation #{i}"
        )

        print(
            "Name:",
            recommendation["name"]
        )

        print(
            "Source:",
            recommendation["source"]
        )

        print(
            "Predicted CO2 Reduction:",
            recommendation[
                "predicted_co2_reduction"
            ]
        )

        print(
            "Cost:",
            recommendation["cost"]
        )

        print(
            "Savings:",
            recommendation["savings"]
        )

        print(
            "ROI:",
            recommendation["roi"]
        )

        print(
            "Feasibility:",
            recommendation["feasibility"]
        )

        print(
            "Final Score:",
            recommendation["score"]
        )

        print("----------------------------")