"""
Emergency Response Priority Engine.
Member 3: Computes transparent weighted response priority and ranks affected zones.
Saves results to outputs/priority_results.json.
"""
import sys
import json
from pathlib import Path
import pandas as pd
import numpy as np
import joblib

# Allow absolute imports from project root
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from config.settings import (
    PRIORITY_RESULTS_PATH,
    IMPACT_RESULTS_PATH,
    PRIORITY_WEIGHTS,
    PRIORITY_MODEL_PATH,
    OUTPUTS_DIR
)


def compute_priority_score(
    risk_score: float,
    population_norm: float,
    infra_norm: float,
    accessibility_norm: float
) -> float:
    """
    Weighted scoring formula required by Feature 3:
    Priority Score =
      40% Risk +
      25% Population +
      20% Critical Infrastructure +
      15% Accessibility (Urgency due to isolation / low accessibility)
    """
    # Low accessibility indicates higher isolation urgency
    isolation_urgency = (1.0 - accessibility_norm) * 100.0

    score = (
        (PRIORITY_WEIGHTS["risk"] * risk_score) +
        (PRIORITY_WEIGHTS["population"] * population_norm * 100.0) +
        (PRIORITY_WEIGHTS["critical_infrastructure"] * infra_norm * 100.0) +
        (PRIORITY_WEIGHTS["accessibility"] * isolation_urgency)
    )
    return round(float(np.clip(score, 0.0, 100.0)), 2)


def get_priority_level(score: float) -> str:
    """Classify priority score into operational response tiers."""
    if score >= 80.0:
        return "CRITICAL"
    elif score >= 65.0:
        return "HIGH"
    elif score >= 45.0:
        return "MEDIUM"
    else:
        return "LOW"


def run_priority_ranking(
    impact_json_path: Path = IMPACT_RESULTS_PATH,
    output_path: Path = PRIORITY_RESULTS_PATH
) -> list:
    """
    Rank all zones based on multi-factor disaster priority score.
    Optionally enriches with ML response priority if disaster_priority_model.pkl exists.
    """
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Load Impact Results
    if not impact_json_path.exists():
        print(f"[WARN] {impact_json_path} not found. Using fallback mock impacts.")
        impacts = [
            {"zone_id": "Z-KOL-03", "zone_name": "Kolkata South East Lowlands", "population": 85000, "total_population": 165000, "hospitals": 4, "schools": 14, "risk_score": 93.4, "accessibility_score": 0.35},
            {"zone_id": "Z-KOL-01", "zone_name": "Kolkata North & Riverbank", "population": 72000, "total_population": 142000, "hospitals": 6, "schools": 18, "risk_score": 86.2, "accessibility_score": 0.45},
            {"zone_id": "Z-KOL-04", "zone_name": "Behala Corridor", "population": 65000, "total_population": 185000, "hospitals": 5, "schools": 16, "risk_score": 71.5, "accessibility_score": 0.50},
            {"zone_id": "Z-KOL-02", "zone_name": "Kolkata Central", "population": 45000, "total_population": 210000, "hospitals": 12, "schools": 25, "risk_score": 64.8, "accessibility_score": 0.65},
            {"zone_id": "Z-KOL-05", "zone_name": "Salt Lake Uplands", "population": 12000, "total_population": 120000, "hospitals": 8, "schools": 22, "risk_score": 24.1, "accessibility_score": 0.90},
        ]
    else:
        with open(impact_json_path, "r", encoding="utf-8") as f:
            impacts = json.load(f)

    # Normalization baselines across current district
    max_pop = max([item.get("population", item.get("affected_population", 1)) for item in impacts] or [1])
    max_infra = max([item.get("hospitals", 0) * 2 + item.get("schools", 0) for item in impacts] or [1])

    # Check for ML priority classifier model
    ml_model = None
    if PRIORITY_MODEL_PATH.exists():
        try:
            ml_model = joblib.load(PRIORITY_MODEL_PATH)
        except Exception as e:
            print(f"[WARN] Failed to load {PRIORITY_MODEL_PATH}: {e}")

    ranked_zones = []
    for item in impacts:
        zid = item.get("zone_id", item.get("zone", "A01"))
        risk = float(item.get("risk_score", 50.0))
        pop = float(item.get("population", item.get("affected_population", 10000)))
        infra_count = float(item.get("hospitals", 1) * 2 + item.get("schools", 2))
        access = float(item.get("accessibility_score", 0.5))

        pop_norm = min(pop / max(max_pop, 1), 1.0)
        infra_norm = min(infra_count / max(max_infra, 1), 1.0)

        score = compute_priority_score(risk, pop_norm, infra_norm, access)
        level = get_priority_level(score)

        # ML priority prediction if model available
        ml_priority = None
        if ml_model is not None:
            try:
                # features: ["final_risk_score", "Population", "affected_population", "total_health_facilities", "total_schools"]
                X_sample = pd.DataFrame([{
                    "final_risk_score": risk,
                    "Population": item.get("total_population", pop * 1.5),
                    "affected_population": pop,
                    "total_health_facilities": item.get("total_hospitals", item.get("hospitals", 2)),
                    "total_schools": item.get("total_schools", item.get("schools", 5))
                }])
                ml_priority = str(ml_model.predict(X_sample)[0])
            except Exception:
                ml_priority = None

        ranked_zones.append({
            "zone_id": zid,
            "zone_name": item.get("zone_name", zid),
            "district": item.get("district", "KOLKATA"),
            "risk_score": risk,
            "affected_population": int(pop),
            "critical_infrastructure_count": int(infra_count),
            "accessibility_score": access,
            "priority_score": score,
            "priority_level": level,
            "ml_predicted_priority": ml_priority,
            "weights_used": PRIORITY_WEIGHTS
        })

    # Sort descending by priority score
    ranked_zones.sort(key=lambda x: x["priority_score"], reverse=True)

    # Assign rank index
    for idx, item in enumerate(ranked_zones, start=1):
        item["priority_rank"] = idx

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(ranked_zones, f, indent=2)

    print(f"[OK] Emergency priority ranking saved to {output_path} ({len(ranked_zones)} zones)")
    return ranked_zones


if __name__ == "__main__":
    run_priority_ranking()
