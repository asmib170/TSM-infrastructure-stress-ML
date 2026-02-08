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

# Importing evaluation metric
from sklearn.metrics import mean_squared_error

# Importing pickle to save the trained model
import pickle



# Database connection

# Defining the SQLite database name
DB_NAME = "tsm_infrastructure.db"

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
X = data_encoded.drop(columns=["stress_score"])
y = data_encoded["stress_score"]



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

    # Storing performance
    model_performance[model_name] = rmse

    # Printing model performance
    print(f"{model_name} RMSE: {rmse:.4f}")



# Selecting and saving the best model

# Identifying the model with the lowest RMSE
best_model_name = min(model_performance, key=model_performance.get)
best_model = models[best_model_name]

# Creating the models directory if it does not exist
os.makedirs("models", exist_ok=True)

# Saving the best model to disk
with open("models/best_model.pkl", "wb") as file:
    pickle.dump(best_model, file)

print(f"\n Best model selected: {best_model_name}")
print(" Model saved successfully in the models folder.")
