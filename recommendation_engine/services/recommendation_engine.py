from .candidate_generator import generate_candidates
from .ml_predictor import predict_co2_reduction
from .score_calculator import calculate_roi, calculate_score


def generate_recommendations(
    emissions, ranked_sources, max_results=3, interventions=None
):

    candidates = generate_candidates(
        ranked_sources, interventions=interventions
    )

    if not candidates:
        return []

    results = []

    predictions = []

    for intervention in candidates:

        predicted_reduction = (
            predict_co2_reduction(
                emissions,
                intervention
            )
        )

        roi = calculate_roi(
            intervention["cost"],
            intervention["savings"]
        )

        predictions.append({
            "intervention": intervention,
            "predicted_reduction":
                predicted_reduction,
            "roi": roi
        })

    co2_values = [
        item["predicted_reduction"]
        for item in predictions
    ]

    roi_values = [
        item["roi"]
        for item in predictions
    ]

    min_co2 = min(co2_values)
    max_co2 = max(co2_values)

    min_roi = min(roi_values)
    max_roi = max(roi_values)

    for item in predictions:

        intervention = item["intervention"]

        co2_score = (
            (item["predicted_reduction"] - min_co2)
            / (max_co2 - min_co2)
            if max_co2 != min_co2
            else 1
        )

        roi_score = (
            (item["roi"] - min_roi)
            / (max_roi - min_roi)
            if max_roi != min_roi
            else 1
        )

        final_score = calculate_score(
            co2_score,
            roi_score,
            intervention["feasibility"]
        )


        results.append({

            "id":
                intervention["id"],

            "name":
                intervention["name"],

            "source":
                intervention["source"],

            "predicted_co2_reduction":
                item["predicted_reduction"],

            "cost":
                intervention["cost"],

            "savings":
                intervention["savings"],

            "roi":
                item["roi"],

            "feasibility":
                intervention["feasibility"],

            "score":
                final_score
        })

    results.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return results[:max_results]