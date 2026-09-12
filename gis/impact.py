"""
GIS Impact Engine.
Member 2: Computes spatial intersections for affected population and critical infrastructure.
Saves results to outputs/impact_results.json.
"""
import sys
import json
from pathlib import Path
import pandas as pd
import numpy as np

# Allow absolute imports from project root
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from config.settings import (
    IMPACT_RESULTS_PATH,
    RISK_PREDICTIONS_PATH,
    SAMPLE_DATA_DIR,
    OUTPUTS_DIR
)

# Optional GeoPandas / Shapely integration
try:
    import geopandas as gpd
    from shapely.geometry import Point, Polygon
    HAS_GEOPANDAS = True
except ImportError:
    HAS_GEOPANDAS = False


def calculate_affected_metrics(zone_data: dict, risk_score: float) -> dict:
    """
    Calculate affected population and vulnerable infrastructure based on risk severity.
    Higher risk score -> higher fraction of population and infrastructure compromised.
    """
    total_pop = zone_data.get("population", 50000)
    total_hospitals = zone_data.get("hospitals", 2)
    total_schools = zone_data.get("schools", 5)
    total_roads = int(zone_data.get("roads_km", 10))
    total_bridges = zone_data.get("bridges", 1)

    # Affected fraction scales with risk score (0-100)
    risk_factor = min(max(risk_score / 100.0, 0.05), 0.95)
    affected_pop = int(total_pop * (risk_factor ** 1.2))

    # Vulnerable infrastructure under current flood depth/risk
    at_risk_hospitals = max(int(np.ceil(total_hospitals * risk_factor * 0.7)), 0)
    at_risk_schools = max(int(np.ceil(total_schools * risk_factor * 0.8)), 0)
    compromised_roads = max(int(np.ceil(total_roads * risk_factor * 0.5)), 0)
    compromised_bridges = max(int(np.ceil(total_bridges * risk_factor * 0.6)), 0)

    return {
        "zone": zone_data.get("zone_id", "A01"),
        "zone_id": zone_data.get("zone_id", "A01"),
        "zone_name": zone_data.get("zone_name", "Zone"),
        "district": zone_data.get("district", "KOLKATA"),
        "state": zone_data.get("state", "WEST BENGAL"),
        "latitude": zone_data.get("latitude", 22.5726),
        "longitude": zone_data.get("longitude", 88.3639),
        "total_population": total_pop,
        "population": affected_pop,  # Contract field: affected population
        "affected_population": affected_pop,
        "hospitals": at_risk_hospitals,  # Contract field: hospitals affected
        "total_hospitals": total_hospitals,
        "schools": at_risk_schools,      # Contract field: schools affected
        "total_schools": total_schools,
        "roads": compromised_roads,      # Contract field: roads affected
        "bridges": compromised_bridges,  # Contract field: bridges affected
        "risk_score": risk_score,
        "accessibility_score": zone_data.get("accessibility_score", 0.5)
    }


def run_impact_analysis(
    risk_csv_path: Path = RISK_PREDICTIONS_PATH,
    zones_json_path: Path = None,
    output_path: Path = IMPACT_RESULTS_PATH
) -> list:
    """
    Run spatial impact analysis on predicted risk zones.
    TODO: Ingest real ISRO Bhuvan flood extent polygons or OpenStreetMap amenity layers.
    """
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Load predicted risk scores
    if not risk_csv_path.exists():
        print(f"[WARN] {risk_csv_path} not found. Running mock fallback.")
        risk_df = pd.DataFrame([
            {"zone_id": "Z-KOL-03", "risk_score": 93.4, "risk_level": "VERY HIGH"},
            {"zone_id": "Z-KOL-01", "risk_score": 86.2, "risk_level": "VERY HIGH"},
            {"zone_id": "Z-KOL-04", "risk_score": 71.5, "risk_level": "HIGH"},
            {"zone_id": "Z-KOL-02", "risk_score": 64.8, "risk_level": "HIGH"},
            {"zone_id": "Z-KOL-05", "risk_score": 24.1, "risk_level": "LOW"},
        ])
    else:
        risk_df = pd.read_csv(risk_csv_path)

    risk_map = dict(zip(risk_df["zone_id"], risk_df["risk_score"]))

    # 2. Load zone definitions
    zones_file = zones_json_path or (SAMPLE_DATA_DIR / "sample_zones.json")
    with open(zones_file, "r", encoding="utf-8") as f:
        zones_data = json.load(f)

    impact_results = []
    for zone in zones_data:
        zid = zone.get("zone_id")
        score = risk_map.get(zid, 50.0)
        impact = calculate_affected_metrics(zone, score)
        impact_results.append(impact)

    # Save output contract
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(impact_results, f, indent=2)

    print(f"[OK] Impact analysis saved to {output_path} ({len(impact_results)} zones)")
    return impact_results


if __name__ == "__main__":
    run_impact_analysis()
