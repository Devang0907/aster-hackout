import os
import joblib
import pandas as pd

from sklearn.model_selection import KFold, cross_validate

from recommendation_engine.models.recommendation_model import get_models


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

print("Loading dataset...")

df = pd.read_csv(DATASET_PATH)

print(f"Dataset rows: {len(df)}")


# --------------------------------------------------
# Check required columns
# --------------------------------------------------

required_columns = FEATURES + [TARGET]

missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing_columns:
    raise ValueError(
        f"Dataset is missing columns: {missing_columns}"
    )


# --------------------------------------------------
# Remove invalid / missing rows
# --------------------------------------------------

df = df.dropna(
    subset=required_columns
)

print(
    f"Rows after removing missing values: "
    f"{len(df)}"
)


# --------------------------------------------------
# Prepare X and y
# --------------------------------------------------

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


# --------------------------------------------------
# Load models
# --------------------------------------------------

models = get_models()

results = []


# --------------------------------------------------
# Evaluate models
# --------------------------------------------------

print("\nTraining and evaluating models...")


for name, model in models.items():

    print(f"\nEvaluating: {name}")

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
        return_train_score=True,
        n_jobs=-1
    )


    # ----------------------------------------------
    # Training MAE
    # ----------------------------------------------

    train_mae = (
        -scores[
            "train_neg_mean_absolute_error"
        ].mean()
    )


    # ----------------------------------------------
    # Validation MAE
    # ----------------------------------------------

    validation_mae = (
        -scores[
            "test_neg_mean_absolute_error"
        ].mean()
    )


    # ----------------------------------------------
    # Validation RMSE
    # ----------------------------------------------

    validation_rmse = (
        -scores[
            "test_neg_root_mean_squared_error"
        ].mean()
    )


    # ----------------------------------------------
    # Validation R²
    # ----------------------------------------------

    validation_r2 = (
        scores[
            "test_r2"
        ].mean()
    )


    # ----------------------------------------------
    # Overfitting difference
    # ----------------------------------------------

    overfit_gap = (
        validation_mae
        - train_mae
    )


    results.append({

        "name":
            name,

        "train_mae":
            train_mae,

        "validation_mae":
            validation_mae,

        "validation_rmse":
            validation_rmse,

        "validation_r2":
            validation_r2,

        "overfit_gap":
            overfit_gap
    })


# --------------------------------------------------
# Display model comparison
# --------------------------------------------------

print("\n")
print("=" * 55)
print("MODEL COMPARISON")
print("=" * 55)


for result in results:

    print(
        f"\nModel: "
        f"{result['name']}"
    )

    print(
        f"Train MAE:        "
        f"{result['train_mae']:.2f}"
    )

    print(
        f"Validation MAE:   "
        f"{result['validation_mae']:.2f}"
    )

    print(
        f"Validation RMSE:  "
        f"{result['validation_rmse']:.2f}"
    )

    print(
        f"Validation R²:    "
        f"{result['validation_r2']:.4f}"
    )

    print(
        f"Overfit Gap:      "
        f"{result['overfit_gap']:.2f}"
    )


# --------------------------------------------------
# Select best model
#
# Lowest Validation MAE wins.
#
# Validation MAE measures how far predictions are
# from actual values on unseen validation data.
# --------------------------------------------------

best_result = min(
    results,
    key=lambda x:
        x["validation_mae"]
)


best_model_name = (
    best_result["name"]
)

best_model = (
    models[
        best_model_name
    ]
)


# --------------------------------------------------
# Train selected model on entire dataset
# --------------------------------------------------

print("\n")
print("=" * 55)
print("TRAINING FINAL MODEL")
print("=" * 55)

print(
    f"\nSelected model: "
    f"{best_model_name}"
)

best_model.fit(
    X,
    y
)


# --------------------------------------------------
# Save trained model
# --------------------------------------------------

joblib.dump(
    best_model,
    MODEL_PATH
)


# --------------------------------------------------
# Final output
# --------------------------------------------------

print("\n")
print("=" * 55)
print("BEST MODEL")
print("=" * 55)

print(
    f"\nSelected Model: "
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
    f"Train MAE: "
    f"{best_result['train_mae']:.2f}"
)

print(
    f"Overfit Gap: "
    f"{best_result['overfit_gap']:.2f}"
)

print(
    f"\nModel saved to:"
)

print(
    MODEL_PATH
)

print(
    "\nTraining completed successfully."
)