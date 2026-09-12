"""
Data loader utilities for reading system outputs and sample datasets safely.
Provides graceful fallbacks so Streamlit never crashes on missing files.
"""
import sys
import json
from pathlib import Path
import pandas as pd

# Allow absolute imports from project root
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from config.settings import (
    RISK_PREDICTIONS_PATH,
    IMPACT_RESULTS_PATH,
    SHELTER_RESULTS_PATH,
    PRIORITY_RESULTS_PATH,
    ROUTE_RESULTS_PATH,
    SAMPLE_DATA_DIR
)


def load_risk_predictions() -> tuple[pd.DataFrame, bool]:
    """
    Load risk predictions from outputs/risk_predictions.csv.
    Returns (DataFrame, is_sample_data).
    """
    if RISK_PREDICTIONS_PATH.exists():
        try:
            df = pd.read_csv(RISK_PREDICTIONS_PATH)
            if not df.empty:
                return df, False
        except Exception as e:
            print(f"[WARN] Failed reading risk_predictions.csv: {e}")

    # Fallback to sample data
    sample_file = SAMPLE_DATA_DIR / "sample_zones.json"
    if sample_file.exists():
        with open(sample_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        df = pd.DataFrame(data)
        # Add baseline risk columns if missing
        if "risk_score" not in df.columns:
            df["risk_score"] = [86.2, 64.8, 93.4, 71.5, 24.1]
            df["risk_level"] = ["VERY HIGH", "HIGH", "VERY HIGH", "HIGH", "LOW"]
            df["risk_probability"] = [0.862, 0.648, 0.934, 0.715, 0.241]
        return df, True

    # Extreme minimal fallback
    df = pd.DataFrame([
        {"zone_id": "Z-01", "zone_name": "Sector Alpha", "district": "KOLKATA", "risk_score": 90.0, "risk_level": "VERY HIGH", "rainfall_mm": 220.0, "risk_probability": 0.90}
    ])
    return df, True


def load_impact_results() -> tuple[list, bool]:
    """
    Load impact results from outputs/impact_results.json.
    Returns (list_of_dicts, is_sample_data).
    """
    if IMPACT_RESULTS_PATH.exists():
        try:
            with open(IMPACT_RESULTS_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                if data:
                    return data, False
        except Exception as e:
            print(f"[WARN] Failed reading impact_results.json: {e}")

    # Fallback mock impacts
    return [
        {
            "zone": "Z-KOL-03", "zone_id": "Z-KOL-03", "zone_name": "Kolkata South East Lowlands",
            "district": "KOLKATA", "latitude": 22.5180, "longitude": 88.3900,
            "population": 155000, "total_population": 165000,
            "hospitals": 4, "total_hospitals": 4, "schools": 14, "total_schools": 14,
            "roads": 36, "bridges": 5, "risk_score": 93.4, "accessibility_score": 0.35
        },
        {
            "zone": "Z-KOL-01", "zone_id": "Z-KOL-01", "zone_name": "Kolkata North & Riverbank",
            "district": "KOLKATA", "latitude": 22.5958, "longitude": 88.3639,
            "population": 122000, "total_population": 142000,
            "hospitals": 5, "total_hospitals": 6, "schools": 15, "total_schools": 18,
            "roads": 42, "bridges": 4, "risk_score": 86.2, "accessibility_score": 0.45
        },
        {
            "zone": "Z-KOL-04", "zone_id": "Z-KOL-04", "zone_name": "Behala Corridor",
            "district": "KOLKATA", "latitude": 22.4985, "longitude": 88.3180,
            "population": 131000, "total_population": 185000,
            "hospitals": 4, "total_hospitals": 5, "schools": 12, "total_schools": 16,
            "roads": 44, "bridges": 3, "risk_score": 71.5, "accessibility_score": 0.50
        }
    ], True


def load_shelter_results() -> tuple[list, bool]:
    """
    Load shelter recommendations from outputs/shelter.json.
    Returns (list_of_dicts, is_sample_data).
    """
    if SHELTER_RESULTS_PATH.exists():
        try:
            with open(SHELTER_RESULTS_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                if data:
                    return data, False
        except Exception as e:
            print(f"[WARN] Failed reading shelter.json: {e}")

    return [
        {
            "zone_id": "Z-KOL-03", "shelter_name": "Salt Lake Stadium Indoor Complex",
            "shelter_latitude": 22.5697, "shelter_longitude": 88.4063,
            "distance_km": 3.2, "shelter_risk": "LOW",
            "total_capacity": 5000, "available_capacity": 4150,
            "suitability_score": 89.2, "status": "RECOMMENDED"
        }
    ], True


def load_priority_results() -> tuple[list, bool]:
    """
    Load emergency priority ranking from outputs/priority_results.json.
    Returns (list_of_dicts, is_sample_data).
    """
    if PRIORITY_RESULTS_PATH.exists():
        try:
            with open(PRIORITY_RESULTS_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                if data:
                    return data, False
        except Exception as e:
            print(f"[WARN] Failed reading priority_results.json: {e}")

    return [
        {
            "priority_rank": 1, "zone_id": "Z-KOL-03", "zone_name": "Kolkata South East Lowlands",
            "priority_score": 94.2, "priority_level": "CRITICAL",
            "risk_score": 93.4, "affected_population": 155000, "critical_infrastructure_count": 18
        },
        {
            "priority_rank": 2, "zone_id": "Z-KOL-01", "zone_name": "Kolkata North Riverbank",
            "priority_score": 87.5, "priority_level": "HIGH",
            "risk_score": 86.2, "affected_population": 122000, "critical_infrastructure_count": 20
        },
        {
            "priority_rank": 3, "zone_id": "Z-KOL-04", "zone_name": "Behala Corridor",
            "priority_score": 72.1, "priority_level": "HIGH",
            "risk_score": 71.5, "affected_population": 131000, "critical_infrastructure_count": 16
        }
    ], True


def load_route_results() -> tuple[dict, bool]:
    """
    Load rescue routes from outputs/route.json.
    Returns (dict, is_sample_data).
    """
    if ROUTE_RESULTS_PATH.exists():
        try:
            with open(ROUTE_RESULTS_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                if data:
                    return data, False
        except Exception as e:
            print(f"[WARN] Failed reading route.json: {e}")

    # Fallback route payload
    return {
        "origin": {"name": "High Priority Zone (Kolkata South East)", "latitude": 22.5180, "longitude": 88.3900},
        "destination": {"name": "Salt Lake Stadium Relief Hub", "latitude": 22.5697, "longitude": 88.4063},
        "routes": {
            "fast_route": {
                "title": "Route A (Fastest via River Road)",
                "distance_km": 8.5,
                "travel_time_min": 15.2,
                "flood_risk_level": "HIGH FLOOD RISK",
                "recommendation": "NOT RECOMMENDED",
                "warning": "Passes through submerged river causeway",
                "coordinates": [[22.5180, 88.3900], [22.5400, 88.3850], [22.5550, 88.3950], [22.5697, 88.4063]]
            },
            "safe_route": {
                "title": "Route B (Highland Bypass)",
                "distance_km": 13.8,
                "travel_time_min": 26.0,
                "flood_risk_level": "LOW FLOOD RISK",
                "recommendation": "RECOMMENDED ALTERNATIVE",
                "warning": "Zero inundation risk on elevated bypass",
                "coordinates": [[22.5180, 88.3900], [22.5330, 88.4150], [22.5600, 88.4250], [22.5697, 88.4063]]
            },
            "optimal_route": {
                "title": "Route C (Risk-Aware Recommended)",
                "distance_km": 11.6,
                "travel_time_min": 22.4,
                "flood_risk_level": "LOW FLOOD RISK",
                "recommendation": "RECOMMENDED PRIMARY",
                "warning": "Optimal trade-off between safety and travel speed",
                "coordinates": [[22.5180, 88.3900], [22.5300, 88.4050], [22.5500, 88.4120], [22.5697, 88.4063]]
            }
        },
        "recommended_route_id": "ROUTE_OPTIMAL"
    }, True


def load_rainfall_data() -> pd.DataFrame:
    """Load IMD rainfall observations from data/sample/sample_rainfall.csv."""
    rain_path = SAMPLE_DATA_DIR / "sample_rainfall.csv"
    if rain_path.exists():
        return pd.read_csv(rain_path)
    return pd.DataFrame([
        {"District": "KOLKATA", "Rainfall_mm": 215.4, "Warning_Level": "RED"}
    ])
