"""
Configuration and constants for Disaster Early Warning & Rescue Intelligence Platform.
"""
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
SAMPLE_DATA_DIR = DATA_DIR / "sample"

MODELS_DIR = BASE_DIR / "models"
OUTPUTS_DIR = BASE_DIR / "outputs"

# Model File Paths
SGD_MODEL_PATH = MODELS_DIR / "sgd_model.pkl"
XGB_MODEL_PATH = MODELS_DIR / "xgb_model.pkl"
PRIORITY_MODEL_PATH = MODELS_DIR / "disaster_priority_model.pkl"

# Output Contract File Paths
RISK_PREDICTIONS_PATH = OUTPUTS_DIR / "risk_predictions.csv"
IMPACT_RESULTS_PATH = OUTPUTS_DIR / "impact_results.json"
SHELTER_RESULTS_PATH = OUTPUTS_DIR / "shelter.json"
PRIORITY_RESULTS_PATH = OUTPUTS_DIR / "priority_results.json"
ROUTE_RESULTS_PATH = OUTPUTS_DIR / "route.json"

# Risk Thresholds
RISK_THRESHOLDS = {
    "LOW": (0, 25),
    "MODERATE": (26, 50),
    "HIGH": (51, 75),
    "VERY HIGH": (76, 100),
}

# Feature 3: Priority Weights Contract
PRIORITY_WEIGHTS = {
    "risk": 0.40,
    "population": 0.25,
    "critical_infrastructure": 0.20,
    "accessibility": 0.15,
}

# UI / Map Defaults (Default centered at an Indian disaster hotspot, e.g. Kolkata / Gangetic Delta)
DEFAULT_MAP_CENTER = [22.5726, 88.3639]
DEFAULT_ZOOM = 11

# Risk Level Colors
RISK_COLORS = {
    "LOW": "#2ECC71",       # Green
    "MODERATE": "#F1C40F",  # Yellow
    "HIGH": "#E67E22",      # Orange
    "VERY HIGH": "#E74C3C", # Red
    "CRITICAL": "#96281B"   # Dark Red
}
