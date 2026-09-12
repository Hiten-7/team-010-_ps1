"""
Risk Prediction Inference Engine.
Member 1: Generates risk probabilities, 0-100 risk scores, and categorical risk levels.
Saves results to outputs/risk_predictions.csv.
"""
import sys
import json
from pathlib import Path
import joblib
import pandas as pd
import numpy as np

# Allow absolute imports from project root
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from config.settings import (
    SGD_MODEL_PATH,
    XGB_MODEL_PATH,
    RISK_PREDICTIONS_PATH,
    SAMPLE_DATA_DIR,
    OUTPUTS_DIR
)
from ml.features import extract_features, compute_risk_score


def load_best_model():
    """
    Load primary XGBoost model if available, fallback to SGD model,
    or return None for rule-based calculation.
    """
    if XGB_MODEL_PATH.exists():
        try:
            return joblib.load(XGB_MODEL_PATH), "XGBoost (Primary)"
        except Exception as e:
            print(f"[WARN] Failed to load XGB model: {e}")

    if SGD_MODEL_PATH.exists():
        try:
            return joblib.load(SGD_MODEL_PATH), "SGDClassifier (Baseline)"
        except Exception as e:
            print(f"[WARN] Failed to load SGD model: {e}")

    return None, "Heuristic Rule Fallback"


def run_risk_prediction(input_zones_path: Path = None, output_path: Path = RISK_PREDICTIONS_PATH) -> pd.DataFrame:
    """
    Run risk inference for disaster zones and write outputs/risk_predictions.csv.
    TODO: Plug in real-time feeds from IMD API or satellite flood extent shapefiles.
    """
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Load zones data
    if input_zones_path and Path(input_zones_path).exists():
        target_path = Path(input_zones_path)
    else:
        target_path = SAMPLE_DATA_DIR / "sample_zones.json"

    if target_path.suffix == ".json":
        with open(target_path, "r", encoding="utf-8") as f:
            zones_data = json.load(f)
        df_zones = pd.DataFrame(zones_data)
    else:
        df_zones = pd.read_csv(target_path)

    # 2. Extract features
    X = extract_features(df_zones)

    # 3. Model Inference
    model, model_name = load_best_model()

    if model is not None:
        try:
            probabilities = model.predict_proba(X)[:, 1]
        except Exception:
            # If decision function only
            df_scores = model.decision_function(X)
            probabilities = 1.0 / (1.0 + np.exp(-df_scores))
    else:
        # Fallback physics/heuristic estimation based on rainfall, river proximity, elevation
        rainfall_ratio = np.clip(df_zones["rainfall_mm"] / 250.0, 0.0, 1.5)
        elevation_inv = 1.0 / (np.maximum(df_zones["elevation_m"], 1.0) / 4.0 + 1.0)
        river_inv = 1.0 / (np.maximum(df_zones["river_proximity_km"], 0.1) / 1.5 + 1.0)
        hist_idx = df_zones.get("historical_flood_index", 0.5)

        raw_est = 0.35 * rainfall_ratio + 0.25 * elevation_inv + 0.20 * river_inv + 0.20 * hist_idx
        probabilities = np.clip(raw_est, 0.05, 0.98)

    # 4. Construct Output DataFrame
    results = []
    for idx, row in df_zones.iterrows():
        prob = float(probabilities[idx])
        score, level = compute_risk_score(prob)

        results.append({
            "zone_id": row.get("zone_id", f"Z-{idx+1:02d}"),
            "zone_name": row.get("zone_name", f"Zone {idx+1}"),
            "district": row.get("district", "KOLKATA"),
            "state": row.get("state", "WEST BENGAL"),
            "latitude": float(row.get("latitude", 22.5726)),
            "longitude": float(row.get("longitude", 88.3639)),
            "rainfall_mm": float(row.get("rainfall_mm", 0.0)),
            "risk_probability": round(prob, 4),
            "risk_score": score,
            "risk_level": level,
            "model_used": model_name
        })

    out_df = pd.DataFrame(results)
    out_df = out_df.sort_values(by="risk_score", ascending=False).reset_index(drop=True)
    out_df.to_csv(output_path, index=False)
    print(f"[OK] Risk predictions written to {output_path} ({len(out_df)} zones)")
    return out_df


if __name__ == "__main__":
    run_risk_prediction()
