"""
SGDClassifier training script (Baseline Model).
Member 1: Train baseline model and serialize to models/sgd_model.pkl.
"""
import sys
from pathlib import Path
import joblib
import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import accuracy_score, classification_report

# Allow absolute imports from project root
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from config.settings import SGD_MODEL_PATH, SAMPLE_DATA_DIR, MODELS_DIR
from ml.features import extract_features


def generate_synthetic_training_data(n_samples: int = 1000, random_state: int = 42) -> pd.DataFrame:
    """Generate realistic synthetic training data matching Indian flood conditions."""
    np.random.seed(random_state)

    rainfall = np.random.gamma(shape=3.0, scale=35.0, size=n_samples) # 20mm - 300mm+
    hist_flood = np.random.uniform(0.1, 0.95, size=n_samples)
    elevation = np.random.uniform(2.0, 50.0, size=n_samples)
    drainage = np.random.uniform(0.1, 0.9, size=n_samples)
    river_dist = np.random.exponential(scale=3.0, size=n_samples) + 0.1

    df = pd.DataFrame({
        "rainfall_mm": rainfall,
        "historical_flood_index": hist_flood,
        "elevation_m": elevation,
        "drainage_density": drainage,
        "river_proximity_km": river_dist
    })

    # Ground truth flood risk logic
    # Flood is likely if high rain, low elevation, close to river, poor drainage
    risk_metric = (
        0.35 * (rainfall / 150.0) +
        0.25 * (1.0 / (elevation / 5.0 + 1.0)) +
        0.20 * (1.0 / (river_dist / 1.5 + 1.0)) +
        0.20 * (1.0 - drainage)
    )
    # Binary flood event (1 = High Risk Flood Occurred, 0 = Safe)
    prob = 1.0 / (1.0 + np.exp(-5.0 * (risk_metric - 0.55)))
    df["flood_occurred"] = (np.random.uniform(0, 1, size=n_samples) < prob).astype(int)

    return df


def train_sgd_model(data_path: Path = None, save_path: Path = SGD_MODEL_PATH):
    """
    Train SGDClassifier with log_loss for calibrated probability estimation.
    TODO: Connect real IMD rainfall and historical Bhuvan flood datasets.
    """
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    print("=== Training SGDClassifier (Baseline Model) ===")
    if data_path and Path(data_path).exists():
        print(f"Loading dataset from {data_path}...")
        raw_df = pd.read_csv(data_path)
    else:
        print("Using synthetic monsoon training dataset...")
        raw_df = generate_synthetic_training_data(n_samples=2500)

    X = extract_features(raw_df)
    y = raw_df["flood_occurred"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("classifier", SGDClassifier(
            loss="log_loss",
            penalty="l2",
            alpha=1e-4,
            max_iter=2000,
            tol=1e-3,
            class_weight="balanced",
            random_state=42
        ))
    ])

    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"SGD Test Accuracy: {acc * 100:.2f}%")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, zero_division=0))

    joblib.dump(pipeline, save_path)
    print(f"[OK] SGD Model saved successfully to: {save_path}")
    return pipeline


if __name__ == "__main__":
    train_sgd_model()
