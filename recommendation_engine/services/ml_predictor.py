import os
import joblib
import pandas as pd


# --------------------------------------------------
# Model path
# --------------------------------------------------

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "ml",
    "model.pkl"
)


# --------------------------------------------------
# Load model once when application starts
# --------------------------------------------------

model = joblib.load(MODEL_PATH)


# --------------------------------------------------
# Predict CO2 reduction
# --------------------------------------------------

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

    prediction = model.predict(
        features
    )

    # CO2 reduction should never be negative
    predicted_reduction = max(
        0,
        float(prediction[0])
    )

    return predicted_reduction