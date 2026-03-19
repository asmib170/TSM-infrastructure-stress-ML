# Importing SQLite to connect and read data from the database
import sqlite3

# Importing pandas for data handling and preprocessing
import pandas as pd

# Importing numpy for numerical operations
import numpy as np

# Importing os to handle folder and file operations
import os

# Importing train-test split utility
from sklearn.model_selection import train_test_split

# Importing regression models
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor

# Importing evaluation metrics
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

# Importing pickle to save the trained model
import pickle

# Importing json to store evaluation metrics
import json

# Importing registry update function from Model folder
from Model.registry_utils import update_registry


# -----------------------------
# BOOSTING MODELS (OPTIONAL)
# -----------------------------

# Trying to import boosting models and skipping them if the libraries are unavailable.
try:
    from xgboost import XGBRegressor
    from catboost import CatBoostRegressor
    BOOSTING_AVAILABLE = True

# Falling back cleanly if the optional boosting libraries are not installed.
except:
    BOOSTING_AVAILABLE = False
    print("Boosting models skipped because xgboost / catboost are not installed.")


# -----------------------------
# PATH SETUP
# -----------------------------

# Getting the directory where this train_model.py file exists.
CURRENT_DIR = os.path.dirname(__file__)

# Moving one level upward so the code can correctly reference the project root.
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))

# Defining the database path from the project root.
DB_PATH = os.path.join(PROJECT_ROOT, "tsm_infrastructure.db")

# Defining the artifacts folder path where trained outputs will be stored.
ARTIFACTS_DIR = os.path.join(PROJECT_ROOT, "artifacts")

# Creating the artifacts folder if it does not already exist.
os.makedirs(ARTIFACTS_DIR, exist_ok=True)


# -----------------------------
# LOAD DATA
# -----------------------------

# Connecting to the SQLite database.
conn = sqlite3.connect(DB_PATH)

# Loading the infrastructure usage table into a pandas DataFrame.
query = "SELECT * FROM infrastructure_usage"
data = pd.read_sql(query, conn)

# Closing the database connection after loading the data.
conn.close()


# -----------------------------
# DATA PREPROCESSING
# -----------------------------

# Dropping the ID column because it is only an identifier and should not be used for prediction.
data = data.drop(columns=["id"])

# Converting the categorical columns into one-hot encoded numeric columns.
# Important syntax: drop_first=True avoids unnecessary dummy-column redundancy.
data_encoded = pd.get_dummies(
    data,
    columns=["resource_type", "day_of_week", "time_slot", "exam_phase"],
    drop_first=True
)

# Defining the input features by removing both stress_score and booking_requests.
# Important logic: stress_score depends on booking_requests, so keeping it would create leakage.
X = data_encoded.drop(columns=["stress_score", "booking_requests"])

# Defining booking_requests as the prediction target.
y = data_encoded["booking_requests"]


# -----------------------------
# TRAIN-TEST SPLIT
# -----------------------------

# Splitting the data into training and test sets for fair evaluation.
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)


# -----------------------------
# MODEL DEFINITIONS
# -----------------------------

# Initializing the baseline regression models for comparison.
models = {
    "Linear Regression": LinearRegression(),
    "Decision Tree": DecisionTreeRegressor(random_state=42),
    "Random Forest": RandomForestRegressor(n_estimators=100, random_state=42)
}

# Adding boosting models if the optional libraries are available.
if BOOSTING_AVAILABLE:

    # Adding XGBoost with tuned parameters.
    models["XGBoost"] = XGBRegressor(
        n_estimators=200,
        learning_rate=0.08,
        max_depth=6,
        subsample=0.9,
        colsample_bytree=0.9,
        random_state=42
    )

    # Adding CatBoost with tuned parameters and early stopping support.
    models["CatBoost"] = CatBoostRegressor(
        iterations=5000,
        learning_rate=0.03,
        depth=6,
        loss_function="RMSE",
        eval_metric="RMSE",
        l2_leaf_reg=6,
        subsample=0.8,
        random_strength=1,
        bagging_temperature=1,
        od_type="Iter",
        od_wait=200,
        verbose=False,
        random_seed=42
    )


# -----------------------------
# MODEL TRAINING & EVALUATION
# -----------------------------

# Creating a dictionary to store the evaluation metrics of each model.
model_performance = {}

# Looping through each model and training/evaluating it.
for model_name, model in models.items():

    # Using a validation set for CatBoost so early stopping and best-iteration selection can work.
    if model_name == "CatBoost":
        model.fit(X_train, y_train, eval_set=(X_test, y_test), use_best_model=True)

    # Training all other models normally.
    else:
        model.fit(X_train, y_train)

    # Generating predictions on the test set.
    predictions = model.predict(X_test)

    # Calculating RMSE to penalize larger errors more strongly.
    rmse = np.sqrt(mean_squared_error(y_test, predictions))

    # Calculating MAE as the average absolute error.
    mae = mean_absolute_error(y_test, predictions)

    # Calculating R² to measure explained variance.
    r2 = r2_score(y_test, predictions)

    # Calculating WAPE as a stable percentage-style error metric.
    # Important logic: WAPE is more suitable than MAPE here because booking demand can be very small or zero.
    wape = np.sum(np.abs(y_test - predictions)) / np.sum(np.abs(y_test))

    # Storing the metrics for this model.
    model_performance[model_name] = {
        "rmse": float(rmse),
        "mae": float(mae),
        "r2": float(r2),
        "wape": float(wape)
    }

    # Printing the metrics so model performance is visible in the terminal.
    print(f"{model_name} | RMSE: {rmse:.4f} | MAE: {mae:.4f} | R2: {r2:.4f} | WAPE: {wape:.4f}")


# -----------------------------
# BEST MODEL SELECTION
# -----------------------------

# Selecting the best model based on the lowest RMSE.
best_model_name = min(model_performance, key=lambda k: model_performance[k]["rmse"])

# Extracting the actual trained best model object.
best_model = models[best_model_name]


# -----------------------------
# SAVE MODEL
# -----------------------------

# Creating a model bundle so the dashboard can load both the model and the exact feature order.
model_bundle = {
    "model": best_model,
    "feature_columns": list(X.columns),
    "best_model_name": best_model_name
}

# Defining the path where the best model bundle will be stored.
MODEL_PATH = os.path.join(ARTIFACTS_DIR, "best_model.pkl")

# Saving the model bundle to disk using pickle.
with open(MODEL_PATH, "wb") as file:
    pickle.dump(model_bundle, file)

# Printing a confirmation message after saving the model.
print(f"\nBest model selected: {best_model_name}")
print("Model saved successfully in artifacts folder.")


# -----------------------------
# SAVE METRICS
# -----------------------------

# Generating predictions from the best model for residual analysis.
best_predictions = best_model.predict(X_test)

# Calculating residuals as actual minus predicted.
residuals = (y_test - best_predictions).astype(float).tolist()

# Creating the metrics payload for dashboard display.
metrics = {
    "metrics": model_performance,
    "best_model": best_model_name,
    "residuals": residuals
}

# Defining the metrics output path inside the artifacts folder.
METRICS_PATH = os.path.join(ARTIFACTS_DIR, "metrics.json")

# Saving the metrics payload to JSON format.
with open(METRICS_PATH, "w") as f:
    json.dump(metrics, f, indent=2)

# Printing a confirmation message after saving the metrics.
print("metrics.json saved successfully in artifacts folder.")


# -----------------------------
# UPDATE REGISTRY
# -----------------------------

# Extracting the best-model evaluation values for registry logging.
best_rmse = model_performance[best_model_name]["rmse"]
best_mae = model_performance[best_model_name]["mae"]
best_r2 = model_performance[best_model_name]["r2"]

# Updating the model registry with the latest training run.
update_registry(
    model_name=best_model_name,
    target="booking_requests",
    rmse=best_rmse,
    mae=best_mae,
    r2=best_r2,
    notes="Weekly retrain. Metrics logged automatically."
)

# Printing a confirmation message after updating the registry.
print("model_registry.json updated with this training run.")