"""
Safe Shelter Recommendation Engine.
Member 2: Evaluates relief shelters based on distance, capacity, safety, and accessibility.
Saves results to outputs/shelter.json.
"""
import sys
import json
import math
from pathlib import Path

# Allow absolute imports from project root
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from config.settings import (
    SHELTER_RESULTS_PATH,
    SAMPLE_DATA_DIR,
    OUTPUTS_DIR
)


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great-circle distance in kilometers between two GPS coordinates."""
    r = 6371.0  # Earth's radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2.0) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2.0) ** 2
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return round(r * c, 2)


def score_shelter(shelter: dict, zone_lat: float, zone_lon: float, zone_pop: int) -> tuple[float, float]:
    """
    Score a shelter for an affected zone.
    Higher score = better candidate.
    """
    dist_km = haversine_distance(zone_lat, zone_lon, shelter["latitude"], shelter["longitude"])

    # Risk penalty (LOW = 1.0, MODERATE = 0.6, HIGH = 0.2)
    risk_multipliers = {"LOW": 1.0, "MODERATE": 0.6, "HIGH": 0.2, "CRITICAL": 0.05}
    risk_factor = risk_multipliers.get(shelter.get("shelter_risk", "LOW"), 0.7)

    # Capacity sufficiency
    avail_cap = shelter.get("available_capacity", 500)
    capacity_ratio = min(avail_cap / max(zone_pop * 0.1, 100), 2.0)

    # Proximity score (shorter distance = higher score)
    dist_score = max(0.0, 10.0 - dist_km) / 10.0

    # Composite recommendation score
    suitability_score = (0.40 * dist_score) + (0.35 * risk_factor) + (0.25 * min(capacity_ratio, 1.0))
    return suitability_score, dist_km


def recommend_shelters(
    zones_path: Path = None,
    shelters_path: Path = None,
    output_path: Path = SHELTER_RESULTS_PATH
) -> list:
    """
    Match each affected zone to its optimal, safe shelter.
    TODO: Integrate live NDEM / district collectorate shelter occupancy and food supply feeds.
    """
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

    zones_file = zones_path or (SAMPLE_DATA_DIR / "sample_zones.json")
    shelters_file = shelters_path or (SAMPLE_DATA_DIR / "sample_shelters.json")

    with open(zones_file, "r", encoding="utf-8") as f:
        zones = json.load(f)
    with open(shelters_file, "r", encoding="utf-8") as f:
        shelters = json.load(f)

    recommendations = []

    for z in zones:
        z_lat, z_lon = z.get("latitude", 22.5726), z.get("longitude", 88.3639)
        z_pop = z.get("population", 50000)

        best_shelter = None
        best_score = -1.0
        best_dist = 999.0

        for s in shelters:
            score, dist = score_shelter(s, z_lat, z_lon, z_pop)
            if score > best_score:
                best_score = score
                best_dist = dist
                best_shelter = s

        recommendations.append({
            "zone_id": z.get("zone_id"),
            "zone_name": z.get("zone_name"),
            "district": z.get("district", "KOLKATA"),
            "recommended_shelter_id": best_shelter["shelter_id"],
            "shelter_name": best_shelter["name"],
            "shelter_latitude": best_shelter["latitude"],
            "shelter_longitude": best_shelter["longitude"],
            "distance_km": best_dist,
            "shelter_risk": best_shelter.get("shelter_risk", "LOW"),
            "total_capacity": best_shelter.get("total_capacity", 1000),
            "available_capacity": best_shelter.get("available_capacity", 500),
            "suitability_score": round(best_score * 100, 1),
            "status": "RECOMMENDED" if best_score > 0.4 else "BACKUP"
        })

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(recommendations, f, indent=2)

    print(f"[OK] Shelter recommendations saved to {output_path} ({len(recommendations)} zones)")
    return recommendations


if __name__ == "__main__":
    recommend_shelters()
