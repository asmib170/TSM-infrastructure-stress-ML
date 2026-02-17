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


# Trying to import boosting models (will skip if not installed)
try:

    # Importing XGBoost regressor
    from xgboost import XGBRegressor

    # Importing CatBoost regressor
    from catboost import CatBoostRegressor

    # Enabling boosting models since imports succeeded
    BOOSTING_AVAILABLE = True

except:

    # Disabling boosting models if libraries are not installed
    BOOSTING_AVAILABLE = False

    # Printing a message so the user knows why boosting was skipped
    print(" Boosting models skipped because xgboost / catboost are not installed.")


# Database connection

# Defining the SQLite database name (keeping same absolute DB path as generator and dashboard)
DB_NAME = r"C:\Users\batto\OneDrive\Desktop\TSM_infrastructure_stress_ML\tsm_infrastructure.db"

# Connecting to the SQLite database
conn = sqlite3.connect(DB_NAME)

# Reading infrastructure usage data into a DataFrame
query = "SELECT * FROM infrastructure_usage"
data = pd.read_sql(query, conn)

# Closing the database connection
conn.close()


# Data preprocessing

# Dropping the ID column as it does not contribute to prediction
data = data.drop(columns=["id"])

# Converting categorical columns into numerical format using one-hot encoding
data_encoded = pd.get_dummies(
    data,
    columns=["resource_type", "day_of_week", "time_slot", "exam_phase"],
    drop_first=True
)

# Defining feature variables (X) and target variable (y)

# Removing both stress_score and booking_requests from features to avoid leakage
X = data_encoded.drop(columns=["stress_score", "booking_requests"])

# Setting booking_requests as the target to predict demand
y = data_encoded["booking_requests"]


# Train-test split

# Splitting the dataset into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)


# Model training and evaluation

# Initializing the models
models = {
    "Linear Regression": LinearRegression(),
    "Decision Tree": DecisionTreeRegressor(random_state=42),
    "Random Forest": RandomForestRegressor(n_estimators=100, random_state=42)
}

# Adding boosting models
if BOOSTING_AVAILABLE:

    # Adding XGBoost model
    models["XGBoost"] = XGBRegressor(
        n_estimators=200,
        learning_rate=0.08,
        max_depth=6,
        subsample=0.9,
        colsample_bytree=0.9,
        random_state=42
    )

    # Adding CatBoost model
    models["CatBoost"] = CatBoostRegressor(
        iterations=300,
        learning_rate=0.08,
        depth=6,
        random_state=42,
        verbose=0
    )

# Dictionary to store model performance
model_performance = {}

# Training and evaluating each model
for model_name, model in models.items():

    # Training the model
    model.fit(X_train, y_train)

    # Making predictions on the test set
    predictions = model.predict(X_test)

    # Calculating RMSE
    rmse = np.sqrt(mean_squared_error(y_test, predictions))

    # Calculating MAE
    mae = mean_absolute_error(y_test, predictions)

    # Calculating R2 score
    r2 = r2_score(y_test, predictions)

    # Storing performance values
    model_performance[model_name] = {
        "rmse": float(rmse),
        "mae": float(mae),
        "r2": float(r2)
    }

    # Printing model performance
    print(f"{model_name} | RMSE: {rmse:.4f} | MAE: {mae:.4f} | R2: {r2:.4f}")



# Selecting and saving the best model

# Identifying the model with the lowest RMSE
# Identifying the model with the lowest RMSE
best_model_name = min(model_performance, key=lambda k: model_performance[k]["rmse"])
best_model = models[best_model_name]

# Creating the models directory if it does not exist
os.makedirs("models", exist_ok=True)

# Creating a model bundle so dashboard can align columns correctly
model_bundle = {
    "model": best_model,
    "feature_columns": list(X.columns),
    "best_model_name": best_model_name
}

# Saving the best model bundle to disk
with open("models/best_model.pkl", "wb") as file:
    pickle.dump(model_bundle, file)

print(f"\n Best model selected: {best_model_name}")
print(" Model saved successfully in the models folder.")

# Importing json to store evaluation metrics
import json

# Generating predictions for residual analysis using the best model
best_predictions = best_model.predict(X_test)

# Calculating residuals (Actual - Predicted)
residuals = (y_test - best_predictions).astype(float).tolist()

# Saving evaluation metrics and residuals for dashboard display
metrics = {
    "metrics": model_performance,
    "best_model": best_model_name,
    "residuals": residuals
}

with open("models/metrics.json", "w") as f:
    json.dump(metrics, f, indent=2)
