# models/train_models.py
"""
Trains real scikit-learn classifiers on real public clinical datasets and
pickles the fitted pipelines used by the Flask app at runtime.

Datasets (all real, public, citable):
  1. Pima Indians Diabetes Database (NIDDK, 768 patients)
  2. Statlog/Cleveland-style Heart Disease dataset (1190 patients)
  3. UCI Chronic Kidney Disease dataset (cleaned subset, 158 patients)
  4. Breast Cancer Wisconsin (Diagnostic) dataset (scikit-learn built-in, 569 patients)

Run whenever a dataset changes: python3 train_models.py
"""
import pandas as pd
import numpy as np
import pickle
import json
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.calibration import CalibratedClassifierCV
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.metrics import brier_score_loss, roc_auc_score

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE, "data")
MODEL_DIR = os.path.join(BASE, "models")

REPORT = {}


def get_feature_importances(fitted_clf, feature_order):
    """Extracts a real per-feature importance ranking from whatever model type was fit."""
    base_clf = fitted_clf
    # CalibratedClassifierCV wraps the real estimator inside calibrated_classifiers_
    if hasattr(fitted_clf, "calibrated_classifiers_"):
        base_clf = fitted_clf.calibrated_classifiers_[0].estimator

    if hasattr(base_clf, "feature_importances_"):
        scores = base_clf.feature_importances_
    elif hasattr(base_clf, "coef_"):
        scores = np.abs(base_clf.coef_[0])
    else:
        return []

    total = scores.sum() or 1.0
    ranked = sorted(zip(feature_order, scores / total), key=lambda x: -x[1])
    return [{"feature": f, "importance": round(float(s), 4)} for f, s in ranked]


def train_and_save(name, X, y, feature_order, model_filename, model=None):
    """
    Fits a real classifier, CALIBRATES its probability outputs against held-out
    folds (so 'confidence' reflects true observed frequencies rather than raw
    model votes), reports honest accuracy/AUC/calibration-error, and pickles
    the final calibrated pipeline plus a feature-importance ranking.
    """
    if model is None:
        model = RandomForestClassifier(n_estimators=200, max_depth=6, random_state=42, class_weight="balanced")

    base_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
        ("clf", model),
    ])

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    # Uncalibrated reference fit, purely to report raw vs. calibrated performance honestly
    base_pipeline.fit(X_train, y_train)
    raw_test_acc = base_pipeline.score(X_test, y_test)
    cv_scores = cross_val_score(base_pipeline, X, y, cv=5)

    # Calibrated pipeline: wraps the classifier with cross-validated probability
    # calibration (Platt/sigmoid scaling) so predict_proba reflects real-world
    # frequencies, not just raw tree-vote ratios.
    calibrated_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
        ("clf", CalibratedClassifierCV(type(model)(**model.get_params()), method="sigmoid",
                                        cv=StratifiedKFold(n_splits=5, shuffle=True, random_state=42))),
    ])
    calibrated_pipeline.fit(X_train, y_train)
    calibrated_proba = calibrated_pipeline.predict_proba(X_test)[:, 1]
    calibrated_acc = calibrated_pipeline.score(X_test, y_test)
    try:
        auc = roc_auc_score(y_test, calibrated_proba)
    except ValueError:
        auc = None
    brier = brier_score_loss(y_test, calibrated_proba)

    # Refit the CALIBRATED pipeline on all available data for deployment
    final_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
        ("clf", CalibratedClassifierCV(type(model)(**model.get_params()), method="sigmoid",
                                        cv=StratifiedKFold(n_splits=5, shuffle=True, random_state=42))),
    ])
    final_pipeline.fit(X, y)

    out_path = os.path.join(MODEL_DIR, model_filename)
    with open(out_path, "wb") as f:
        pickle.dump(final_pipeline, f)

    # Feature importances computed from an uncalibrated fit on all data (calibration
    # wrapping obscures direct access to tree/coef importances on the deployed object)
    importance_ref = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
        ("clf", type(model)(**model.get_params())),
    ])
    importance_ref.fit(X, y)
    importances = get_feature_importances(importance_ref.named_steps["clf"], feature_order)

    REPORT[name] = {
        "n_samples": len(X),
        "n_features": len(feature_order),
        "feature_order": feature_order,
        "feature_importances": importances,
        "held_out_test_accuracy_uncalibrated": round(float(raw_test_acc), 4),
        "held_out_test_accuracy_calibrated": round(float(calibrated_acc), 4),
        "5fold_cv_mean_accuracy": round(float(cv_scores.mean()), 4),
        "5fold_cv_std": round(float(cv_scores.std()), 4),
        "held_out_auc": round(float(auc), 4) if auc is not None else None,
        "held_out_brier_score": round(float(brier), 4),
        "model_file": model_filename,
    }
    auc_str = f"{auc:.3f}" if auc is not None else "n/a"
    print(f"[{name}] n={len(X)} features={len(feature_order)} "
          f"acc(raw)={raw_test_acc:.3f} acc(calibrated)={calibrated_acc:.3f} "
          f"auc={auc_str} brier={brier:.4f} -> {model_filename}")


# ---------------------------------------------------------------------------
# 1. DIABETES (Pima Indians Diabetes Database - real NIDDK data, 768 records)
#    Feature order matches what the chat collects: 6 specialty fields + 2 global (BloodPressure, Age)
# ---------------------------------------------------------------------------
df = pd.read_csv(os.path.join(DATA_DIR, "diabetes.csv"))
feature_order = ["Pregnancies", "Glucose", "BloodPressure", "SkinThickness",
                  "Insulin", "BMI", "DiabetesPedigreeFunction", "Age"]
# Zeros in these physiological columns are documented missing-value placeholders in this dataset
for col in ["Glucose", "BloodPressure", "SkinThickness", "Insulin", "BMI"]:
    df[col] = df[col].replace(0, np.nan)
X = df[feature_order]
y = df["Outcome"]
train_and_save("diabetes", X, y, feature_order, "diabetes_model.pkl")

# ---------------------------------------------------------------------------
# 2. HEART DISEASE (Cleveland-style heart dataset, 1190 records)
#    Feature order: 8 specialty fields + 3 global (age, sex, resting bp s)
# ---------------------------------------------------------------------------
df = pd.read_csv(os.path.join(DATA_DIR, "heart.csv"))
feature_order = ["age", "sex", "chest pain type", "resting bp s", "cholesterol", "fasting blood sugar",
                  "resting ecg", "max heart rate", "exercise angina", "oldpeak", "ST slope"]
X = df[feature_order]
y = df["target"]
train_and_save("heart", X, y, feature_order, "heart_model.pkl")

# ---------------------------------------------------------------------------
# 3. CHRONIC KIDNEY DISEASE (UCI CKD dataset, cleaned version, 158 records)
#    Reduced to the 10 most clinically predictive lab/history fields + global Age,
#    matching the high-yield markers reported in the CKD literature.
# ---------------------------------------------------------------------------
df = pd.read_csv(os.path.join(DATA_DIR, "kidney_disease.csv"))
binary_map = {"yes": 1, "no": 0, "normal": 1, "abnormal": 0, "present": 1, "notpresent": 0,
              "good": 1, "poor": 0}
for col in df.columns:
    if df[col].dtype == object or pd.api.types.is_string_dtype(df[col]):
        df[col] = df[col].astype(str).str.strip().map(binary_map)
feature_order = ["Age", "Blood Pressure", "Specific Gravity", "Albumin", "Sugar",
                  "Blood Glucose Random", "Blood Urea", "Serum Creatinine", "Hemoglobin",
                  "Hypertension", "Diabetes Mellitus"]
X = df[feature_order]
y = df["Class"]
train_and_save("kidney", X, y, feature_order, "kidney_model.pkl")

# ---------------------------------------------------------------------------
# 4. BREAST CANCER (Wisconsin Diagnostic dataset, scikit-learn built-in, 569 records)
#    Reduced to the 10 "mean" tumor measurements (full diagnostic panel has 30; a
#    chat flow asking 30 numeric questions is unusable, and the 10 mean features
#    alone still carry strong real signal).
# ---------------------------------------------------------------------------
df = pd.read_csv(os.path.join(DATA_DIR, "breast_cancer.csv"))
feature_order = ["mean radius", "mean texture", "mean perimeter", "mean area", "mean smoothness",
                  "mean compactness", "mean concavity", "mean concave points", "mean symmetry",
                  "mean fractal dimension"]
X = df[feature_order]
# sklearn convention: target 0 = malignant, 1 = benign. Flip so 1 = "positive finding" (malignant),
# consistent with every other disease tab in this app (1 = disease/finding present).
y = (df["target"] == 0).astype(int)
train_and_save("breast_cancer", X, y, feature_order, "breast_cancer_model.pkl",
                model=LogisticRegression(max_iter=2000, class_weight="balanced"))

# ---------------------------------------------------------------------------
with open(os.path.join(MODEL_DIR, "training_report.json"), "w") as f:
    json.dump(REPORT, f, indent=2)

print("\nAll models trained. Report saved to models/training_report.json")
