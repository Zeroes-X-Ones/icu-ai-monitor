"""
train_model.py
--------------
Trains a RandomForestClassifier on historical PatientVitals data
and saves the model + label encoder as .pkl files.

Usage (from project root):
    python -m app.ml.train_model

Or run directly:
    cd backend
    python -m app.ml.train_model

The script reads from the SQLite database, creates synthetic labels
where alert_level is missing, trains the model, and saves:
    backend/app/ml/model.pkl
    backend/app/ml/encoder.pkl
"""

import os
import sys
import random
import joblib
import numpy as np
from datetime import datetime

# -- Path setup ------------------------------------------------------------------
# Allow running from any working directory
_HERE = os.path.dirname(os.path.abspath(__file__))
_BACKEND = os.path.abspath(os.path.join(_HERE, "..", "..", ".."))  # .../backend
if _BACKEND not in sys.path:
    sys.path.insert(0, _BACKEND)

from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# -- Feature / label helpers -----------------------------------------------------

FEATURES = [
    "heart_rate",
    "spo2",
    "respiratory_rate",
    "blood_pressure_systolic",
    "blood_pressure_diastolic",
]

LABEL_MAP = {
    "INFO":     "NORMAL",
    "NORMAL":   "NORMAL",
    "WARNING":  "WARNING",
    "CRITICAL": "CRITICAL",
}


def _alert_to_label(alert_level: str) -> str:
    """Map DB alert_level values -> consistent ML label."""
    return LABEL_MAP.get(str(alert_level).upper(), "NORMAL")


def _derive_label(hr, spo2, rr, bps, bpd) -> str:
    """
    Rule-based fallback label for rows with no/unknown alert_level.
    Mirrors the distress_detector thresholds.
    """
    score = 0
    if spo2 < 88:       score += 45
    elif spo2 < 90:     score += 40
    elif spo2 < 94:     score += 25
    elif spo2 < 96:     score += 10

    if hr > 130:        score += 28
    elif hr > 120:      score += 22
    elif hr > 100:      score += 14
    elif hr < 45:       score += 30
    elif hr < 55:       score += 20

    if rr > 30:         score += 22
    elif rr > 24:       score += 14
    elif rr > 20:       score += 6

    if bps > 180:       score += 20
    elif bps > 160:     score += 15
    elif bps > 140:     score += 10
    elif bps < 80:      score += 25
    elif bps < 90:      score += 18

    # Multi-metric correlation bonuses
    if hr > 100 and spo2 < 94:    score += 15
    if bps < 90 and hr > 100:     score += 18

    score = min(score, 100)
    if score >= 70:   return "CRITICAL"
    if score >= 35:   return "WARNING"
    return "NORMAL"


# -- Synthetic data generation (used when DB has <50 rows) -----------------------

def _generate_synthetic_data(n: int = 2000):
    """
    Generate synthetic vitals data covering all three risk classes.
    This ensures the model can be trained even on a fresh database.
    """
    rows = []
    random.seed(42)
    np.random.seed(42)

    for _ in range(n):
        class_roll = random.random()
        if class_roll < 0.60:       # 60 % NORMAL
            hr  = random.gauss(75, 10)
            spo2 = random.gauss(98, 1.0)
            rr  = random.gauss(16, 2)
            bps = random.gauss(118, 10)
            bpd = random.gauss(75, 7)
        elif class_roll < 0.85:     # 25 % WARNING
            hr  = random.gauss(108, 12)
            spo2 = random.gauss(93.5, 1.5)
            rr  = random.gauss(22, 3)
            bps = random.gauss(148, 15)
            bpd = random.gauss(88, 8)
        else:                       # 15 % CRITICAL
            hr  = random.gauss(128, 15)
            spo2 = random.gauss(87, 2.5)
            rr  = random.gauss(30, 4)
            bps = random.gauss(80, 10)
            bpd = random.gauss(52, 6)

        # Clamp to physiological bounds
        hr  = max(30, min(200, hr))
        spo2 = max(70, min(100, spo2))
        rr  = max(5, min(45, rr))
        bps = max(60, min(220, bps))
        bpd = max(30, min(130, bpd))

        label = _derive_label(hr, spo2, rr, bps, bpd)
        rows.append([hr, spo2, rr, bps, bpd, label])

    return rows


def load_data_from_db():
    """
    Try to load vitals from the SQLite database using raw SQL
    (avoids ORM schema-mismatch errors on older DB files).
    Returns a list of [hr, spo2, rr, bps, bpd, label] rows.
    Falls back to / augments with synthetic data when DB is insufficient.
    """
    rows = []
    try:
        import sqlite3
        # Try common DB filenames in the backend directory
        _candidate_names = ["icu_vitals.db", "icu_monitor.db", "vitals.db"]
        db_path = None
        for _name in _candidate_names:
            _p = os.path.join(_BACKEND, _name)
            if os.path.exists(_p):
                db_path = _p
                break
        if db_path is None:
            # Last resort: one level above backend
            for _name in _candidate_names:
                _p = os.path.join(os.path.dirname(_BACKEND), _name)
                if os.path.exists(_p):
                    db_path = _p
                    break

        if db_path and os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Discover available columns so we never crash on missing ones
            cursor.execute("PRAGMA table_info(patient_vitals)")
            available_cols = {row[1] for row in cursor.fetchall()}

            select_cols = ["heart_rate", "spo2", "blood_pressure_systolic",
                           "blood_pressure_diastolic", "alert_level"]
            rr_available = "respiratory_rate" in available_cols
            if rr_available:
                select_cols.insert(2, "respiratory_rate")

            sql = f"SELECT {', '.join(select_cols)} FROM patient_vitals"
            cursor.execute(sql)

            for row in cursor.fetchall():
                if rr_available:
                    hr, spo2_val, rr, bps, bpd, alert = row
                    rr = rr if rr else 16.0
                else:
                    hr, spo2_val, bps, bpd, alert = row
                    rr = 16.0   # default when column missing

                label = _alert_to_label(alert)
                rows.append([float(hr), float(spo2_val), float(rr),
                             float(bps), float(bpd), label])
            conn.close()
        else:
            print(f"[train_model] DB not found at {db_path} -- using synthetic data only.")

    except Exception as e:
        print(f"[train_model] DB load failed: {e} -- using synthetic data.")

    if len(rows) < 50:
        print(f"[train_model] Only {len(rows)} DB rows -- augmenting with synthetic data.")
        rows.extend(_generate_synthetic_data(2000))

    return rows


# -- Train & save ----------------------------------------------------------------

def train_and_save():
    print("[train_model] Loading data ...")
    rows = load_data_from_db()
    print(f"[train_model] Total samples: {len(rows)}")

    X = np.array([[r[0], r[1], r[2], r[3], r[4]] for r in rows], dtype=float)
    y_raw = [r[5] for r in rows]

    le = LabelEncoder()
    y = le.fit_transform(y_raw)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print("[train_model] Training RandomForestClassifier ...")
    clf = RandomForestClassifier(
        n_estimators=100,
        random_state=42,
        class_weight="balanced",
        n_jobs=-1
    )
    clf.fit(X_train, y_train)

    print("[train_model] Evaluation on held-out test set:")
    y_pred = clf.predict(X_test)
    print(classification_report(y_test, y_pred, target_names=le.classes_))

    # Feature importance summary
    importances = clf.feature_importances_
    for feat, imp in sorted(zip(FEATURES, importances), key=lambda x: -x[1]):
        print(f"  {feat:35s}: {imp:.4f}")

    # Save artefacts alongside this script
    model_path   = os.path.join(_HERE, "model.pkl")
    encoder_path = os.path.join(_HERE, "encoder.pkl")
    joblib.dump(clf, model_path)
    joblib.dump(le,  encoder_path)

    print(f"\n[train_model] Model saved  -> {model_path}")
    print(f"[train_model] Encoder saved -> {encoder_path}")
    return clf, le


if __name__ == "__main__":
    train_and_save()
