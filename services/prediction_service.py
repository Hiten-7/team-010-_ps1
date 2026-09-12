"""
Prediction Service for Disaster Intelligence Platform.
Executes trained XGBoost and SGDClassifier pipelines on dynamic location features,
generates classified risk zones (Low, Moderate, High, Critical), and calculates
the multi-factor 0-100 Disaster Severity Score.
"""
from pathlib import Path
from typing import Dict, Any, List
import joblib
import numpy as np
import pandas as pd

from config.settings import XGB_MODEL_PATH, SGD_MODEL_PATH
from ml.features import extract_features, compute_risk_score


class PredictionService:
    """Runs ML pipelines and calculates dynamic disaster severity scores."""

    def __init__(self):
        self.xgb_model = None
        self.sgd_model = None
        self._load_models()

    def _load_models(self):
        if XGB_MODEL_PATH.exists():
            try:
                self.xgb_model = joblib.load(XGB_MODEL_PATH)
            except Exception as e:
                print(f"[WARN] Could not load {XGB_MODEL_PATH}: {e}")

        if SGD_MODEL_PATH.exists():
            try:
                self.sgd_model = joblib.load(SGD_MODEL_PATH)
            except Exception as e:
                print(f"[WARN] Could not load {SGD_MODEL_PATH}: {e}")

    def predict_risk_zones(
        self,
        location: Dict[str, Any],
        rainfall: Dict[str, Any],
        river: Dict[str, Any],
        historical: Dict[str, Any],
        model_choice: str = "XGBoost"
    ) -> List[Dict[str, Any]]:
        """
        Runs ML prediction for all sub-zones of the location.
        """
        sub_zones = location.get("sub_zones", [])
        base_lat = location.get("latitude", 22.57)
        base_lon = location.get("longitude", 88.36)
        rain_24h = rainfall.get("last24Hours", 80.0)
        hist_index = historical.get("historical_flood_frequency", 0.5)

        # Select model pipeline
        model = self.xgb_model if "XGB" in model_choice.upper() and self.xgb_model else (self.sgd_model or self.xgb_model)
        model_label = "XGBoost (Primary Model)" if model == self.xgb_model and model else "SGDClassifier (Baseline Model)"

        zone_records = []
        for idx, z in enumerate(sub_zones):
            z_lat = round(base_lat + z.get("lat_offset", 0.0), 4)
            z_lon = round(base_lon + z.get("lon_offset", 0.0), 4)
            elev = z.get("elev", location.get("elevation_m", 10.0))
            drainage = z.get("drainage", location.get("drainage_density", 0.45))

            # River proximity varies by sub-zone elevation and layout
            river_prox = 0.3 if elev < 5.0 else (1.5 if elev < 20.0 else 4.5)

            feature_df = pd.DataFrame([{
                "rainfall_mm": rain_24h * (1.1 if elev < 5.0 else 0.95),
                "historical_flood_index": hist_index,
                "elevation_m": elev,
                "drainage_density": drainage,
                "river_proximity_km": river_prox
            }])

            X = extract_features(feature_df)

            if model is not None:
                try:
                    prob = float(model.predict_proba(X)[:, 1][0])
                except Exception:
                    df_s = model.decision_function(X)
                    prob = float(1.0 / (1.0 + np.exp(-df_s[0])))
            else:
                # Fallback calculation
                r_norm = min(rain_24h / 250.0, 1.5)
                e_norm = 1.0 / (max(elev, 1.0) / 5.0 + 1.0)
                prob = np.clip(0.40 * r_norm + 0.35 * e_norm + 0.25 * hist_index, 0.05, 0.98)

            score, level = compute_risk_score(prob)
            if score >= 80.0:
                classified_level = "CRITICAL RISK"
            elif score >= 60.0:
                classified_level = "HIGH RISK"
            elif score >= 40.0:
                classified_level = "MODERATE RISK"
            else:
                classified_level = "LOW RISK"

            # Dynamic reasons
            reasons = []
            if rain_24h > 150.0:
                reasons.append(f"Heavy 24h precipitation ({rain_24h:.1f} mm)")
            if river.get("current_level_m", 0) >= river.get("danger_mark_m", 1):
                reasons.append(f"{river.get('nearest_river')} level at {river.get('current_level_m')}m breaches danger mark")
            if elev < 5.0:
                reasons.append(f"Low elevation ({elev:.1f}m) prone to backflow and canal overflow")
            if hist_index >= 0.6:
                reasons.append("High historical flood recurrence zone")
            if not reasons:
                reasons.append("Stable terrain with standard storm runoff")

            zone_records.append({
                "zone_id": z.get("id", f"Z-{idx+1:02d}"),
                "zone_name": z.get("name", f"Sector {idx+1}"),
                "area_locality": z.get("name"),
                "latitude": z_lat,
                "longitude": z_lon,
                "elevation_m": elev,
                "drainage_density": drainage,
                "river_proximity_km": river_prox,
                "risk_probability": round(prob, 4),
                "risk_score": score,
                "risk_level": classified_level,
                "model_used": model_label,
                "reasons": reasons,
                "pop_weight": z.get("pop_weight", 0.2)
            })

        zone_records.sort(key=lambda x: x["risk_score"], reverse=True)
        return zone_records

    def calculate_severity_score(
        self,
        rainfall_data: Dict[str, Any],
        river_data: Dict[str, Any],
        historical_data: Dict[str, Any],
        avg_zone_risk: float
    ) -> Dict[str, Any]:
        """
        Formula required by specification:
        severityScore =
          rainfallRisk * 0.25 +
          riverRisk * 0.20 +
          populationRisk * 0.15 +
          historicalRisk * 0.15 +
          infrastructureRisk * 0.15 +
          forecastRisk * 0.10
        """
        r_24h = rainfall_data.get("last24Hours", 50.0)
        rainfall_risk = min(max((r_24h / 250.0) * 100.0, 5.0), 100.0)

        # River risk
        diff = river_data.get("difference_m", 0.0)
        if diff >= 0.5:
            river_risk = 95.0
        elif diff >= 0.0:
            river_risk = 82.0
        elif diff >= -0.5:
            river_risk = 65.0
        else:
            river_risk = 30.0

        pop_risk = avg_zone_risk
        hist_risk = historical_data.get("avg_historical_risk", 50.0)
        infra_risk = min(avg_zone_risk * 1.05, 95.0)

        f_48h = rainfall_data.get("forecast48Hours", 80.0)
        forecast_risk = min(max((f_48h / 300.0) * 100.0, 10.0), 100.0)

        final_score = (
            rainfall_risk * 0.25 +
            river_risk * 0.20 +
            pop_risk * 0.15 +
            hist_risk * 0.15 +
            infra_risk * 0.15 +
            forecast_risk * 0.10
        )

        final_score = round(float(np.clip(final_score, 5.0, 99.0)), 1)
        if final_score >= 80.0:
            severity_tier = "CRITICAL THREAT"
            badge_color = "RED"
        elif final_score >= 60.0:
            severity_tier = "HIGH THREAT"
            badge_color = "ORANGE"
        elif final_score >= 40.0:
            severity_tier = "MODERATE THREAT"
            badge_color = "YELLOW"
        else:
            severity_tier = "LOW THREAT"
            badge_color = "GREEN"

        return {
            "score": final_score,
            "tier": severity_tier,
            "badge_color": badge_color,
            "components": {
                "rainfall_risk": round(rainfall_risk, 1),
                "river_risk": round(river_risk, 1),
                "population_risk": round(pop_risk, 1),
                "historical_risk": round(hist_risk, 1),
                "infrastructure_risk": round(infra_risk, 1),
                "forecast_risk": round(forecast_risk, 1)
            }
        }
