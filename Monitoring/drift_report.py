# Importing the os module for interacting with file paths and directories
import os

# Importing the json module for writing the drift report into a JSON file
import json

# Importing sqlite3 for connecting and interacting with the SQLite database
import sqlite3

# Importing the date class from datetime for generating today's date for the report
from datetime import date

# Importing numpy for numerical calculations such as logarithms and clipping values
import numpy as np

# Importing pandas for working with tabular data using DataFrames
import pandas as pd


# -----------------------------
# PATH SETUP (IMPORTANT FIX)
# -----------------------------

# Getting the folder where this script currently exists.
# Since drift_report.py is now inside the Monitoring folder, this gives that folder path.
CURRENT_DIR = os.path.dirname(__file__)

# Moving one level upward to reach the main project root folder.
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))

# Creating the path to the SQLite database file from the project root.
DB_NAME = os.path.join(PROJECT_ROOT, "tsm_infrastructure.db")

# Defining the name of the table from which infrastructure usage data will be read.
TABLE = "infrastructure_usage"

# Defining the folder where drift reports will be stored.
REPORTS_DIR = os.path.join(PROJECT_ROOT, "reports", "drift")


# Defining a function for calculating Population Stability Index (PSI) for numeric columns
def psi_numeric(expected: pd.Series, actual: pd.Series, bins=10) -> float:

    # Cleaning the expected data by dropping missing values and converting the values to float type.
    expected = expected.dropna().astype(float)

    # Cleaning the actual data by dropping missing values and converting the values to float type.
    actual = actual.dropna().astype(float)

    # Checking if either dataset has fewer than 2 unique values and returning 0 because PSI cannot be computed properly.
    if expected.nunique() < 2 or actual.nunique() < 2:
        return 0.0

    # Creating evenly spaced quantile points between 0 and 1 for bin creation.
    quantiles = np.linspace(0, 1, bins + 1)

    # Calculating bin boundaries based on quantiles of the expected distribution.
    cuts = np.unique(expected.quantile(quantiles).values)

    # Checking if the number of cut points is too small and returning 0 if bins cannot be formed properly.
    if len(cuts) < 3:
        return 0.0

    # Splitting the expected values into bins and calculating normalized frequencies.
    exp_counts = pd.cut(expected, bins=cuts, include_lowest=True).value_counts(normalize=True)

    # Splitting the actual values using the same bins and calculating normalized frequencies.
    act_counts = pd.cut(actual, bins=cuts, include_lowest=True).value_counts(normalize=True)

    # Aligning both distributions so that they contain the same bins.
    exp_counts, act_counts = exp_counts.align(act_counts, fill_value=0.0)

    # Defining a small epsilon value to prevent division by zero or log of zero.
    eps = 1e-6

    # Clipping the expected distribution values so they stay between epsilon and 1.
    exp = np.clip(exp_counts.values, eps, 1)

    # Clipping the actual distribution values so they stay between epsilon and 1.
    act = np.clip(act_counts.values, eps, 1)

    # Calculating the PSI value using the PSI formula and returning it as a float.
    return float(np.sum((act - exp) * np.log(act / exp)))


# Defining a function for calculating Population Stability Index (PSI) for categorical columns
def psi_categorical(expected: pd.Series, actual: pd.Series) -> float:

    # Replacing missing values with "NA" and converting values to string type.
    expected = expected.fillna("NA").astype(str)

    # Replacing missing values with "NA" and converting values to string type.
    actual = actual.fillna("NA").astype(str)

    # Calculating the normalized frequency distribution of categories in the expected dataset.
    exp_counts = expected.value_counts(normalize=True)

    # Calculating the normalized frequency distribution of categories in the actual dataset.
    act_counts = actual.value_counts(normalize=True)

    # Aligning both categorical distributions so they contain the same category labels.
    exp_counts, act_counts = exp_counts.align(act_counts, fill_value=0.0)

    # Defining a small epsilon value to prevent mathematical errors.
    eps = 1e-6

    # Clipping expected distribution values between epsilon and 1.
    exp = np.clip(exp_counts.values, eps, 1)

    # Clipping actual distribution values between epsilon and 1.
    act = np.clip(act_counts.values, eps, 1)

    # Calculating the PSI value for categorical distributions.
    return float(np.sum((act - exp) * np.log(act / exp)))


# Creating the main function that will run the drift detection pipeline
def main():

    # Checking whether the database exists before trying to read from it.
    if not os.path.exists(DB_NAME):
        print("Database not found. Run `python -m Data.data_generator` first.")
        return

    # Connecting to the SQLite database using the database path defined earlier.
    con = sqlite3.connect(DB_NAME)

    # Reading the infrastructure usage table into a pandas DataFrame using an SQL query.
    df = pd.read_sql_query(f"SELECT * FROM {TABLE}", con)

    # Closing the database connection after loading the data.
    con.close()

    # Checking whether the table is empty before proceeding.
    if df.empty:
        print("No data found in the database. Run `python -m Data.data_generator` first.")
        return

    # Creating the baseline dataset by selecting rows where week is between 1 and 6.
    pre = df[df["week"].between(1, 6)]

    # Creating the comparison dataset by selecting rows where week is between 7 and 12.
    post = df[df["week"].between(7, 12)]

    # Defining the numeric columns for which drift will be calculated.
    numeric_cols = ["effective_capacity", "booking_requests"]

    # Defining the categorical columns for which drift will be calculated.
    cat_cols = ["resource_type", "day_of_week", "time_slot", "exam_phase"]

    # Creating a dictionary for storing PSI results.
    psi_results = {}

    # Looping through numeric columns and calculating PSI for each column.
    for col in numeric_cols:
        if col in df.columns:
            psi_results[col] = psi_numeric(pre[col], post[col])

    # Looping through categorical columns and calculating PSI for each column.
    for col in cat_cols:
        if col in df.columns:
            psi_results[col] = psi_categorical(pre[col], post[col])

    # Creating a dictionary for storing drift severity flags.
    flags = {}

    # Checking PSI values and assigning drift severity levels.
    for k, v in psi_results.items():
        if v > 0.2:
            flags[k] = "significant"
        elif v > 0.1:
            flags[k] = "moderate"
        else:
            flags[k] = "low"

    # Creating a report dictionary that stores metadata and drift results.
    report = {
        "date": date.today().isoformat(),
        "db": DB_NAME,
        "table": TABLE,
        "windows": {
            "expected": "weeks 1-6",
            "actual": "weeks 7-12"
        },
        "psi": psi_results,
        "flags": flags
    }

    # Creating the drift reports folder if it does not already exist.
    os.makedirs(REPORTS_DIR, exist_ok=True)

    # Creating the output file path for the drift report JSON.
    output_path = os.path.join(REPORTS_DIR, f"drift_{report['date']}.json")

    # Opening the output file in write mode with UTF-8 encoding.
    with open(output_path, "w", encoding="utf-8") as f:

        # Writing the report dictionary into the JSON file with indentation.
        json.dump(report, f, indent=2)

    # Printing a message confirming that the drift report has been saved.
    print(f"Drift report saved: {output_path}")


# Checking if this script is being executed directly and calling the main function
if __name__ == "__main__":
    main()