import os
import json
import sqlite3
from datetime import date
import numpy as np
import pandas as pd

# Ensure output files are written in project directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

DB_NAME = os.path.join(os.path.dirname(__file__), "tsm_infrastructure.db")
TABLE = "infrastructure_usage"


def psi_numeric(expected: pd.Series, actual: pd.Series, bins=10) -> float:
    expected = expected.dropna().astype(float)
    actual = actual.dropna().astype(float)

    if expected.nunique() < 2 or actual.nunique() < 2:
        return 0.0

    quantiles = np.linspace(0, 1, bins + 1)
    cuts = np.unique(expected.quantile(quantiles).values)

    if len(cuts) < 3:
        return 0.0

    exp_counts = pd.cut(expected, bins=cuts, include_lowest=True).value_counts(normalize=True)
    act_counts = pd.cut(actual, bins=cuts, include_lowest=True).value_counts(normalize=True)

    exp_counts, act_counts = exp_counts.align(act_counts, fill_value=0.0)

    eps = 1e-6
    exp = np.clip(exp_counts.values, eps, 1)
    act = np.clip(act_counts.values, eps, 1)

    return float(np.sum((act - exp) * np.log(act / exp)))


def psi_categorical(expected: pd.Series, actual: pd.Series) -> float:
    expected = expected.fillna("NA").astype(str)
    actual = actual.fillna("NA").astype(str)

    exp_counts = expected.value_counts(normalize=True)
    act_counts = actual.value_counts(normalize=True)

    exp_counts, act_counts = exp_counts.align(act_counts, fill_value=0.0)

    eps = 1e-6
    exp = np.clip(exp_counts.values, eps, 1)
    act = np.clip(act_counts.values, eps, 1)

    return float(np.sum((act - exp) * np.log(act / exp)))


def main():
    con = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query(f"SELECT * FROM {TABLE}", con)
    con.close()

    # Define time windows
    pre = df[df["week"].between(1, 6)]
    post = df[df["week"].between(7, 12)]

    numeric_cols = ["effective_capacity", "booking_requests"]
    cat_cols = ["resource_type", "day_of_week", "time_slot", "exam_phase"]

    psi_results = {}

    for col in numeric_cols:
        if col in df.columns:
            psi_results[col] = psi_numeric(pre[col], post[col])

    for col in cat_cols:
        if col in df.columns:
            psi_results[col] = psi_categorical(pre[col], post[col])

    flags = {}
    for k, v in psi_results.items():
        if v > 0.2:
            flags[k] = "significant"
        elif v > 0.1:
            flags[k] = "moderate"
        else:
            flags[k] = "low"

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

    os.makedirs("reports", exist_ok=True)

    output_path = f"reports/drift_{report['date']}.json"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"Drift report saved: {output_path}")


if __name__ == "__main__":
    main()