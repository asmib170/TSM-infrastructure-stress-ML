# Importing json to read/write registry data
import json

# Importing os to handle file paths dynamically
import os

# Importing date to timestamp model versions
from datetime import date


# -----------------------------
# PATH SETUP (VERY IMPORTANT FIX)
# -----------------------------

# Getting current file directory (Model folder)
CURRENT_DIR = os.path.dirname(__file__)

# Defining correct path to model_registry.json inside Model folder
REG_PATH = os.path.join(CURRENT_DIR, "model_registry.json")


# -----------------------------
# VERSION HANDLING
# -----------------------------

def bump_version(prev: str) -> str:
    # If no valid previous version exists, start from v1.0.0
    if not prev or not prev.startswith("v"):
        return "v1.0.0"

    # Removing 'v' and splitting into version parts
    parts = prev[1:].split(".")

    # Ensuring we always have major.minor.patch format
    while len(parts) < 3:
        parts.append("0")

    # Converting to integers
    major, minor, patch = map(int, parts[:3])

    # Incrementing patch version
    patch += 1

    # Returning updated version string
    return f"v{major}.{minor}.{patch}"


# -----------------------------
# UPDATE REGISTRY FUNCTION
# -----------------------------

def update_registry(
    model_name: str,
    target: str,
    rmse: float,
    mae: float,
    r2: float,
    notes: str,
    db_name="tsm_infrastructure.db",
    table="infrastructure_usage"
):

    # Getting today's date
    today = date.today().isoformat()

    # Creating registry file if it doesn't exist
    if not os.path.exists(REG_PATH):
        reg = {
            "project_name": "TSM Infrastructure Stress ML",
            "current_best": {},
            "history": []
        }
    else:
        # Loading existing registry
        with open(REG_PATH, "r", encoding="utf-8") as f:
            reg = json.load(f)

    # Getting previous version (default fallback)
    prev_version = reg.get("current_best", {}).get("version", "v1.0.0")

    # Generating new version
    new_version = bump_version(prev_version)

    # Creating new registry entry
    entry = {
        "version": new_version,
        "date": today,
        "model_name": model_name,
        "target": target,
        "metrics": {
            "rmse": rmse,
            "mae": mae,
            "r2": r2
        },
        "data": {
            "db": db_name,
            "table": table
        },
        "notes": notes
    }

    # Appending new entry to history
    reg["history"].append(entry)

    # Updating current best model
    reg["current_best"] = entry

    # Saving updated registry back to file
    with open(REG_PATH, "w", encoding="utf-8") as f:
        json.dump(reg, f, indent=2)

    # Returning entry for confirmation/debugging
    return entry