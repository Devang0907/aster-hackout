from functools import lru_cache
from pathlib import Path
from typing import Any

import joblib
import pandas as pd

MODEL_PATH = Path(__file__).resolve().parent.parent / "ml" / "model.pkl"
FEATURES = (
    "electricity_emission",
    "diesel_emission",
    "raw_material_emission",
    "waste_emission",
    "transport_emission",
    "cost",
    "savings",
    "feasibility",
)


@lru_cache(maxsize=1)
def _load_model() -> Any:
    if not MODEL_PATH.exists():
        raise RuntimeError(f"recommendation model is missing: {MODEL_PATH}")
    model = joblib.load(MODEL_PATH)
    if int(getattr(model, "n_features_in_", 0)) != len(FEATURES):
        raise RuntimeError("recommendation model has an incompatible feature count")
    model_features = tuple(str(value) for value in getattr(model, "feature_names_in_", ()))
    if model_features and model_features != FEATURES:
        raise RuntimeError("recommendation model has an incompatible feature schema")
    return model


def predict_co2_reduction(emissions, intervention):
    model = _load_model()
    features = pd.DataFrame(
        [
            {
                "electricity_emission": emissions.get("electricity", 0),
                "diesel_emission": emissions.get("diesel", 0),
                "raw_material_emission": emissions.get("raw_material", 0),
                "waste_emission": emissions.get("waste", 0),
                "transport_emission": emissions.get("transport", 0),
                "cost": intervention["cost"],
                "savings": intervention["savings"],
                "feasibility": intervention["feasibility"],
            }
        ],
        columns=FEATURES,
    )
    return max(0.0, float(model.predict(features)[0]))
