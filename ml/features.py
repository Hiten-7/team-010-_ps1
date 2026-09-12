"""
Feature engineering utilities for Disaster Risk Prediction.
Transforms raw meteorological, terrain, and historical data into ML feature matrices.
"""
import pandas as pd
import numpy as np


def extract_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract and engineer features for flood / disaster risk prediction.

    Expected input columns (or reasonable defaults):
    - rainfall_mm: Observed or forecasted 24h rainfall
    - historical_flood_index: Past frequency/vulnerability (0 to 1)
    - elevation_m: Altitude in meters above sea level
    - drainage_density: Drainage quality (0 to 1)
    - river_proximity_km: Distance to nearest active river/canal
    """
    df = df.copy()

    # Fill defaults if columns missing
    if "rainfall_mm" not in df.columns:
        df["rainfall_mm"] = 50.0
    if "historical_flood_index" not in df.columns:
        df["historical_flood_index"] = 0.5
    if "elevation_m" not in df.columns:
        df["elevation_m"] = 10.0
    if "drainage_density" not in df.columns:
        df["drainage_density"] = 0.5
    if "river_proximity_km" not in df.columns:
        df["river_proximity_km"] = 5.0

    # Composite flood susceptibility indicator
    # Higher rainfall + lower elevation + proximity to river -> Higher risk
    elevation_factor = 1.0 / (np.maximum(df["elevation_m"], 1.0) + 1.0)
    proximity_factor = 1.0 / (np.maximum(df["river_proximity_km"], 0.1) + 1.0)
    rainfall_norm = np.clip(df["rainfall_mm"] / 250.0, 0.0, 2.0)

    df["rainfall_elevation_ratio"] = rainfall_norm * elevation_factor * 10.0
    df["river_vulnerability_index"] = df["historical_flood_index"] * proximity_factor * 5.0
    df["drainage_stress_index"] = rainfall_norm * (1.0 - df["drainage_density"])

    feature_cols = [
        "rainfall_mm",
        "historical_flood_index",
        "elevation_m",
        "drainage_density",
        "river_proximity_km",
        "rainfall_elevation_ratio",
        "river_vulnerability_index",
        "drainage_stress_index"
    ]

    return df[feature_cols]


def compute_risk_score(probability: float) -> tuple[float, str]:
    """
    Convert model probability (0.0 - 1.0) to a 0-100 risk score and categorical level.
    Scale:
      0-25:   LOW
      26-50:  MODERATE
      51-75:  HIGH
      76-100: VERY HIGH
    """
    prob = float(np.clip(probability, 0.0, 1.0))
    score = round(prob * 100.0, 2)

    if score <= 25.0:
        level = "LOW"
    elif score <= 50.0:
        level = "MODERATE"
    elif score <= 75.0:
        level = "HIGH"
    else:
        level = "VERY HIGH"

    return score, level
