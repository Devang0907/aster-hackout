import joblib
import os
import pandas as pd


BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "ml",
    "model.pkl"
)

model = joblib.load(MODEL_PATH)


def predict_co2_reduction(
    emissions,
    intervention
):

    features = pd.DataFrame([{
        "electricity_emission":
            emissions["electricity"],

        "diesel_emission":
            emissions["diesel"],

        "raw_material_emission":
            emissions["raw_material"],

        "waste_emission":
            emissions["waste"],

        "transport_emission":
            emissions["transport"],

        "cost":
            intervention["cost"],

        "savings":
            intervention["savings"],

        "feasibility":
            intervention["feasibility"]
    }])

    prediction = model.predict(features)

    return float(prediction[0])