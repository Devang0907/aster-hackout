import joblib
import os

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

    features = [[

        emissions["electricity"],

        emissions["diesel"],

        emissions["raw_material"],

        emissions["waste"],

        emissions["transport"],

        intervention["cost"],

        intervention["savings"],

        intervention["feasibility"]

    ]]

    prediction = model.predict(features)

    return float(prediction[0])