def calculate_roi(cost, savings):
    """
    Calculate Return on Investment.

    ROI = savings / cost
    """

    if cost <= 0:
        return 0.0

    return savings / cost


def calculate_score(
    co2_score,
    roi_score,
    feasibility
):
    """
    Calculate the final recommendation score.

    Weights:
    - CO2 reduction: 50%
    - ROI: 30%
    - Feasibility: 20%
    """

    score = (
        0.50 * co2_score
        + 0.30 * roi_score
        + 0.20 * feasibility
    )

    return score