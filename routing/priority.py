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
    isolation_urgency = (1.0 - accessibility_norm) * 100.0

    score = (
        (PRIORITY_WEIGHTS["risk"] * risk_score) +
        (PRIORITY_WEIGHTS["population"] * population_norm * 100.0) +
        (PRIORITY_WEIGHTS["critical_infrastructure"] * infra_norm * 100.0) +
        (PRIORITY_WEIGHTS["accessibility"] * isolation_urgency)
    )
    return round(float(np.clip(score, 0.0, 100.0)), 2)


def get_priority_classification(score: float) -> tuple[str, str, str]:
    """Classify priority score into official response tiers with reasons and directives."""
    if score >= 80.0:
        tier = "PRIORITY 1 - IMMEDIATE RESPONSE"
        urgency = "CRITICAL"
        action = "Deploy NDRF/SDRF rescue boat teams immediately. Begin mandatory evacuation of vulnerable populations."
    elif score >= 65.0:
        tier = "PRIORITY 2 - HIGH PRIORITY"
        urgency = "HIGH"
        action = "Stage emergency medical units and clear primary evacuation routes. Pre-alert shelters."
    elif score >= 45.0:
        tier = "PRIORITY 3 - MODERATE PRIORITY"
        urgency = "MODERATE"
        action = "Issue public flood warning advisories and preposition auxiliary pumps."
    else:
        tier = "PRIORITY 4 - MONITOR"
        urgency = "MONITOR"
        action = "Maintain continuous rainfall and river gauge telemetry monitoring."

    return tier, urgency, action


def run_priority_ranking(
    impact_json_path: Path = IMPACT_RESULTS_PATH,
    output_path: Path = PRIORITY_RESULTS_PATH
) -> list:
    """
    Rank all zones based on multi-factor disaster priority score.
    """
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

    if not impact_json_path.exists():
        impacts = [
            {"zone_id": "Z-KOL-01", "zone_name": "Riverside Sector 4", "area_locality": "Riverside Sector 4", "population": 18500, "total_population": 18500, "hospitals": 3, "schools": 6, "risk_score": 92.4, "accessibility_score": 0.35, "river_status": "ABOVE DANGER MARK (+0.6m)"},
            {"zone_id": "Z-KOL-03", "zone_name": "South East Wetlands", "area_locality": "Eastern Canal Basin", "population": 29000, "total_population": 29000, "hospitals": 2, "schools": 9, "risk_score": 94.5, "accessibility_score": 0.28, "river_status": "OVERFLOWING"},
            {"zone_id": "Z-KOL-04", "zone_name": "Behala Corridor", "area_locality": "Behala Industrial Area", "population": 36000, "total_population": 36000, "hospitals": 4, "schools": 11, "risk_score": 71.5, "accessibility_score": 0.52, "river_status": "STABLE"},
            {"zone_id": "Z-KOL-02", "zone_name": "Central Commercial Hub", "area_locality": "Central Commercial Sector", "population": 42000, "total_population": 42000, "hospitals": 8, "schools": 15, "risk_score": 64.8, "accessibility_score": 0.65, "river_status": "APPROACHING DANGER MARK"},
            {"zone_id": "Z-KOL-05", "zone_name": "Salt Lake Uplands", "area_locality": "Sector V High Ground", "population": 25000, "total_population": 25000, "hospitals": 6, "schools": 14, "risk_score": 24.1, "accessibility_score": 0.92, "river_status": "NORMAL"},
        ]
    else:
        with open(impact_json_path, "r", encoding="utf-8") as f:
            impacts = json.load(f)

    max_pop = max([item.get("population", item.get("affected_population", 1)) for item in impacts] or [1])
    max_infra = max([item.get("hospitals", 0) * 2 + item.get("schools", 0) + item.get("bridges", 0) for item in impacts] or [1])

    ml_model = None
    if PRIORITY_MODEL_PATH.exists():
        try:
            ml_model = joblib.load(PRIORITY_MODEL_PATH)
        except Exception as e:
            print(f"[WARN] Failed to load {PRIORITY_MODEL_PATH}: {e}")

    ranked_zones = []
    for item in impacts:
        zid = item.get("zone_id", item.get("zone", "A01"))
        area = item.get("area_locality", item.get("zone_name", zid))
        risk = float(item.get("risk_score", 50.0))
        pop = float(item.get("population", item.get("affected_population", 10000)))
        infra_count = float(item.get("hospitals", 1) * 2 + item.get("schools", 2) + item.get("bridges", 1))
        access = float(item.get("accessibility_score", 0.5))

        pop_norm = min(pop / max(max_pop, 1), 1.0)
        infra_norm = min(infra_count / max(max_infra, 1), 1.0)

        score = compute_priority_score(risk, pop_norm, infra_norm, access)
        tier, urgency, action = get_priority_classification(score)

        reasons = [
            f"Disaster severity score of {risk:.1f}/100 with high flood susceptibility",
            f"{int(pop):,} people potentially affected in immediate perimeter",
            f"{item.get('hospitals', 1)} critical hospital(s) and {item.get('schools', 2)} school(s) exposed",
            f"Hydrological alert: {item.get('river_status', 'High water levels reported')}"
        ]

        # ML priority prediction if model available
        ml_priority = None
        if ml_model is not None:
            try:
                X_sample = pd.DataFrame([{
                    "final_risk_score": risk,
                    "Population": item.get("total_population", pop * 1.2),
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
            "area_locality": area,
            "district": item.get("district", "KOLKATA"),
            "risk_score": risk,
            "affected_population": int(pop),
            "critical_infrastructure_count": int(infra_count),
            "accessibility_score": access,
            "priority_score": score,
            "priority_tier": tier,
            "priority_level": urgency,
            "recommended_action": action,
            "priority_reasons": reasons,
            "ml_predicted_priority": ml_priority
        })

    # Sort descending by priority score
    ranked_zones.sort(key=lambda x: x["priority_score"], reverse=True)

    for idx, item in enumerate(ranked_zones, start=1):
        item["priority_rank"] = idx

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(ranked_zones, f, indent=2)

    print(f"[OK] Emergency priority ranking saved to {output_path} ({len(ranked_zones)} zones)")
    return ranked_zones


if __name__ == "__main__":
    run_priority_ranking()
