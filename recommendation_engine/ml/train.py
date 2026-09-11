import os
import joblib
import pandas as pd

from sklearn.model_selection import KFold, cross_validate
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import mean_squared_error
from sklearn.metrics import r2_score

from models.recommendation_model import get_models


# --------------------------------------------------
# Paths
# --------------------------------------------------

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

DATASET_PATH = os.path.join(
    BASE_DIR,
    "ml",
    "dataset.csv"
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "ml",
    "model.pkl"
)


# --------------------------------------------------
# Features
# --------------------------------------------------

FEATURES = [
    "electricity_emission",
    "diesel_emission",
    "raw_material_emission",
    "waste_emission",
    "transport_emission",
    "cost",
    "savings",
    "feasibility"
]

TARGET = "co2_reduction"


# --------------------------------------------------
# Load dataset
# --------------------------------------------------

df = pd.read_csv(DATASET_PATH)

X = df[FEATURES]
y = df[TARGET]


# --------------------------------------------------
# Cross validation
# --------------------------------------------------

cv = KFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)


models = get_models()

results = []


# --------------------------------------------------
# Evaluate models
# --------------------------------------------------

for name, model in models.items():

    scores = cross_validate(
        model,
        X,
        y,
        cv=cv,
        scoring=[
            "neg_mean_absolute_error",
            "neg_root_mean_squared_error",
            "r2"
        ],
        return_train_score=True
    )

    train_mae = -scores["train_neg_mean_absolute_error"].mean()

    validation_mae = -scores[
        "test_neg_mean_absolute_error"
    ].mean()

    validation_rmse = -scores[
        "test_neg_root_mean_squared_error"
    ].mean()

    validation_r2 = scores[
        "test_r2"
    ].mean()

    overfit_gap = validation_mae - train_mae

    results.append({
        "name": name,
        "train_mae": train_mae,
        "validation_mae": validation_mae,
        "validation_rmse": validation_rmse,
        "validation_r2": validation_r2,
        "overfit_gap": overfit_gap
    })


# --------------------------------------------------
# Display results
# --------------------------------------------------

print("\n==========================================")
print("MODEL COMPARISON")
print("==========================================")

for result in results:

    print(f"\nModel: {result['name']}")

    print(
        f"Train MAE: "
        f"{result['train_mae']:.2f}"
    )

    print(
        f"Validation MAE: "
        f"{result['validation_mae']:.2f}"
    )

    print(
        f"Validation RMSE: "
        f"{result['validation_rmse']:.2f}"
    )

    print(
        f"Validation R²: "
        f"{result['validation_r2']:.4f}"
    )

    print(
        f"Overfit Gap: "
        f"{result['overfit_gap']:.2f}"
    )


# --------------------------------------------------
# Select best model
# --------------------------------------------------

# First find models with reasonable overfitting.
#
# Here we use a simple rule:
# validation MAE should not be more than
# 50% worse than training MAE.

acceptable_models = [

    result
    for result in results

    if result["validation_mae"]
    <= result["train_mae"] * 1.5
]


# If no model passes the overfitting rule,
# choose the model with lowest validation MAE.

if acceptable_models:

    best_result = min(
        acceptable_models,
        key=lambda x: x["validation_mae"]
    )

else:

    best_result = min(
        results,
        key=lambda x: x["validation_mae"]
    )


best_model_name = best_result["name"]

best_model = models[best_model_name]


# --------------------------------------------------
# Train selected model on complete dataset
# --------------------------------------------------

best_model.fit(X, y)


# --------------------------------------------------
# Save model
# --------------------------------------------------

joblib.dump(
    best_model,
    MODEL_PATH
)


print("\n==========================================")
print("BEST MODEL")
print("==========================================")

print(
    f"Selected Model: "
    f"{best_model_name}"
)

print(
    f"Validation MAE: "
    f"{best_result['validation_mae']:.2f}"
)

print(
    f"Validation RMSE: "
    f"{best_result['validation_rmse']:.2f}"
)

print(
    f"Validation R²: "
    f"{best_result['validation_r2']:.4f}"
)

print(
    f"Overfit Gap: "
    f"{best_result['overfit_gap']:.2f}"
)

print(
    f"\nModel saved to: {MODEL_PATH}"
)