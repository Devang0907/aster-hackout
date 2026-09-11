from functools import lru_cache
from pathlib import Path
from typing import Any

MODEL_PATH = Path(__file__).resolve().parent.parent / "ml" / "model.pkl"
SOURCE_FEATURES = {
    "electricity": "electricity",
    "diesel": "diesel",
    "raw_material": "raw_material",
    "waste": "waste",
    "transport": "transport",
}


@lru_cache(maxsize=1)
def _load_model() -> Any:
    if not MODEL_PATH.exists():
        return None
    try:
        import joblib
    except ImportError:
        return None
    return joblib.load(MODEL_PATH)


def predict_co2_reduction(emissions, intervention):
    model = _load_model()
    if model is not None:
        features = [[
            emissions.get("electricity", 0),
            emissions.get("diesel", 0),
            emissions.get("raw_material", 0),
            emissions.get("waste", 0),
            emissions.get("transport", 0),
            intervention["cost"],
            intervention["savings"],
            intervention["feasibility"],
        ]]
        return max(0.0, float(model.predict(features)[0]))

    source = SOURCE_FEATURES.get(intervention["source"])
    source_emissions = float(emissions.get(source, 0)) if source else 0.0
    reduction_rate = float(intervention.get("co2_reduction_rate", 0))
    return max(0.0, source_emissions * reduction_rate)