"""
XGBoost training script (Primary / Final Risk Model).
Member 1: Train primary gradient boosted model and serialize to models/xgb_model.pkl.
"""
import sys
from pathlib import Path
import joblib
import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, roc_auc_score, classification_report

# Allow absolute imports from project root
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from config.settings import XGB_MODEL_PATH, MODELS_DIR
from ml.features import extract_features
from ml.train_sgd import generate_synthetic_training_data

# Attempt XGBoost import with graceful fallback to HistGradientBoostingClassifier
try:
    from xgboost import XGBClassifier
    IS_XGBOOST_INSTALLED = True
except ImportError:
    from sklearn.ensemble import HistGradientBoostingClassifier as XGBClassifier
    IS_XGBOOST_INSTALLED = False


def train_xgboost_model(data_path: Path = None, save_path: Path = XGB_MODEL_PATH):
    """
    Train XGBoost (or Scikit-Learn Gradient Boosting fallback) model for risk prediction.
    TODO: Tune hyperparameters against real historical flood datasets from ISRO Bhuvan / NDEM.
    """
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    print("=== Training XGBoost (Primary Model) ===")
    if not IS_XGBOOST_INSTALLED:
        print("[NOTE] 'xgboost' not yet installed; using Scikit-Learn Gradient Boosting fallback.")

    if data_path and Path(data_path).exists():
        print(f"Loading dataset from {data_path}...")
        raw_df = pd.read_csv(data_path)
    else:
        print("Using synthetic monsoon training dataset...")
        raw_df = generate_synthetic_training_data(n_samples=3000)

    X = extract_features(raw_df)
    y = raw_df["flood_occurred"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    if IS_XGBOOST_INSTALLED:
        clf = XGBClassifier(
            n_estimators=150,
            max_depth=5,
            learning_rate=0.08,
            subsample=0.8,
            colsample_bytree=0.8,
            eval_metric="logloss",
            random_state=42
        )
    else:
        clf = XGBClassifier(
            max_iter=150,
            max_depth=5,
            learning_rate=0.08,
            random_state=42
        )

    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("classifier", clf)
    ])

    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)
    y_prob = pipeline.predict_proba(X_test)[:, 1]

    acc = accuracy_score(y_test, y_pred)
    roc = roc_auc_score(y_test, y_prob)
    print(f"Primary Model Accuracy: {acc * 100:.2f}% | ROC-AUC: {roc:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, zero_division=0))

    joblib.dump(pipeline, save_path)
    print(f"[OK] Primary Model saved successfully to: {save_path}")
    return pipeline


if __name__ == "__main__":
    train_xgboost_model()
