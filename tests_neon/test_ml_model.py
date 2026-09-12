import os

import joblib

from recommendation_engine.services.ml_predictor import (
    MODEL_PATH,
    predict_co2_reduction,
)


EMISSIONS = {
    "electricity": 35000.0,
    "diesel": 0.0,
    "raw_material": 92500.0,
    "waste": 500.0,
    "transport": 255000.0,
}


def test_model_file_exists():
    assert os.path.exists(MODEL_PATH)


def test_model_can_be_loaded():
    model = joblib.load(MODEL_PATH)
    assert hasattr(model, "predict")


def test_model_has_expected_features():
    model = joblib.load(MODEL_PATH)

    expected = [
        "electricity_emission",
        "diesel_emission",
        "raw_material_emission",
        "waste_emission",
        "transport_emission",
        "cost",
        "savings",
        "feasibility",
    ]

    if hasattr(model, "feature_names_in_"):
        assert list(model.feature_names_in_) == expected


def test_prediction_is_non_negative():
    intervention = {
        "cost": 60000,
        "savings": 15000,
        "feasibility": 0.60,
    }

    prediction = predict_co2_reduction(
        EMISSIONS,
        intervention,
    )

    assert isinstance(prediction, float)
    assert prediction >= 0
