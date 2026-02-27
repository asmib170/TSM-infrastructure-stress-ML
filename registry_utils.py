import json
import os
from datetime import date

REG_PATH = "model_registry.json"

def bump_version(prev: str) -> str:
    # v1.0.0 -> v1.0.1
    if not prev or not prev.startswith("v"):
        return "v1.0.0"
    parts = prev[1:].split(".")
    while len(parts) < 3:
        parts.append("0")
    major, minor, patch = map(int, parts[:3])
    patch += 1
    return f"v{major}.{minor}.{patch}"

def update_registry(model_name: str, target: str, rmse: float, mae: float, r2: float, notes: str,
                    db_name="tsm_infrastructure.db", table="infrastructure_usage"):
    today = date.today().isoformat()

    # Create file if missing
    if not os.path.exists(REG_PATH):
        reg = {"project_name": "TSM Infrastructure Stress ML", "current_best": {}, "history": []}
    else:
        with open(REG_PATH, "r", encoding="utf-8") as f:
            reg = json.load(f)

    prev_version = reg.get("current_best", {}).get("version", "v1.0.0")
    new_version = bump_version(prev_version)

    entry = {
        "version": new_version,
        "date": today,
        "model_name": model_name,
        "target": target,
        "metrics": {"rmse": rmse, "mae": mae, "r2": r2},
        "data": {"db": db_name, "table": table},
        "notes": notes
    }

    reg["history"].append(entry)
    reg["current_best"] = entry

    with open(REG_PATH, "w", encoding="utf-8") as f:
        json.dump(reg, f, indent=2)

    return entry