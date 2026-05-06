"""
model_loader.py
---------------
Singleton loader for the trained RandomForest model + LabelEncoder.

Public API
----------
load_model()         → loads (model, encoder) once; returns None on failure
predict_risk(feats)  → returns dict:
    {
        "ml_risk"       : "NORMAL" | "WARNING" | "CRITICAL",
        "ml_confidence" : float,   # max class probability
        "ml_available"  : bool,
        "class_probs"   : dict,    # {label: probability}
    }
"""

import os
import logging
from typing import Optional, Tuple, Dict

import joblib
import numpy as np

logger = logging.getLogger(__name__)

# ── Paths ───────────────────────────────────────────────────────────────────────
_HERE        = os.path.dirname(os.path.abspath(__file__))
_MODEL_PATH  = os.path.join(_HERE, "model.pkl")
_ENCODER_PATH = os.path.join(_HERE, "encoder.pkl")

# ── Feature order (MUST match train_model.py) ───────────────────────────────────
FEATURE_NAMES = [
    "heart_rate",
    "spo2",
    "respiratory_rate",
    "blood_pressure_systolic",
    "blood_pressure_diastolic",
]

# ── Singleton state ─────────────────────────────────────────────────────────────
_model   = None
_encoder = None
_loaded  = False


def load_model() -> bool:
    """
    Load model + encoder from disk (once).
    Returns True if successful, False otherwise.
    """
    global _model, _encoder, _loaded

    if _loaded:
        return _model is not None

    if not os.path.exists(_MODEL_PATH):
        logger.warning(
            "[model_loader] model.pkl not found at %s — ML layer disabled. "
            "Run: python -m app.ml.train_model  to generate it.",
            _MODEL_PATH,
        )
        _loaded = True
        return False

    if not os.path.exists(_ENCODER_PATH):
        logger.warning("[model_loader] encoder.pkl not found — ML layer disabled.")
        _loaded = True
        return False

    try:
        _model   = joblib.load(_MODEL_PATH)
        _encoder = joblib.load(_ENCODER_PATH)
        _loaded  = True
        logger.info("[model_loader] ML model loaded successfully from %s", _MODEL_PATH)
        return True
    except Exception as exc:
        logger.error("[model_loader] Failed to load model: %s", exc)
        _loaded = True
        return False


def predict_risk(
    heart_rate: float,
    spo2: float,
    respiratory_rate: float,
    bp_sys: float,
    bp_dia: float,
) -> Dict:
    """
    Predict clinical risk level using the trained RandomForest model.

    Returns
    -------
    {
        "ml_risk"       : str,   # NORMAL | WARNING | CRITICAL
        "ml_confidence" : float, # confidence in the top prediction
        "ml_available"  : bool,  # False when model not loaded (fail-safe)
        "class_probs"   : dict,  # {label: probability} for all classes
    }
    """
    # Ensure model is loaded (idempotent)
    available = load_model()

    if not available or _model is None or _encoder is None:
        return {
            "ml_risk":       None,
            "ml_confidence": 0.0,
            "ml_available":  False,
            "class_probs":   {},
        }

    try:
        # Shape: [[hr, spo2, rr, bps, bpd]]
        X = np.array([[heart_rate, spo2, respiratory_rate, bp_sys, bp_dia]], dtype=float)

        # Raw probability vector
        proba = _model.predict_proba(X)[0]          # shape: (n_classes,)
        class_labels = _encoder.classes_             # e.g. ['CRITICAL', 'NORMAL', 'WARNING']

        # Build a human-readable prob dict
        class_probs = {
            str(label): round(float(p), 4)
            for label, p in zip(class_labels, proba)
        }

        # Top prediction
        top_idx       = int(np.argmax(proba))
        ml_risk       = str(class_labels[top_idx])
        ml_confidence = round(float(proba[top_idx]), 4)

        return {
            "ml_risk":       ml_risk,
            "ml_confidence": ml_confidence,
            "ml_available":  True,
            "class_probs":   class_probs,
        }

    except Exception as exc:
        logger.error("[model_loader] predict_risk failed: %s", exc)
        return {
            "ml_risk":       None,
            "ml_confidence": 0.0,
            "ml_available":  False,
            "class_probs":   {},
        }


def get_feature_importance_text(
    heart_rate: float,
    spo2: float,
    respiratory_rate: float,
    bp_sys: float,
    bp_dia: float,
) -> str:
    """
    Return a human-readable string describing the top two features
    that most influenced the model's prediction.

    Falls back gracefully if model not loaded.
    """
    available = load_model()

    if not available or _model is None:
        return ""

    try:
        importances = _model.feature_importances_  # shape: (5,)
        values = [heart_rate, spo2, respiratory_rate, bp_sys, bp_dia]

        # Pair each feature with its global importance score
        pairs = sorted(
            zip(FEATURE_NAMES, importances, values),
            key=lambda x: -x[1]
        )

        # Build readable labels for top-2 features
        readable = {
            "heart_rate":              _describe_hr(heart_rate),
            "spo2":                    _describe_spo2(spo2),
            "respiratory_rate":        _describe_rr(respiratory_rate),
            "blood_pressure_systolic": _describe_bps(bp_sys),
            "blood_pressure_diastolic": _describe_bpd(bp_dia),
        }

        top2 = [readable.get(name, name) for name, _, _ in pairs[:2]]
        return f"Risk driven by {top2[0]} and {top2[1]}."

    except Exception as exc:
        logger.error("[model_loader] feature importance failed: %s", exc)
        return ""


# ── Readable feature descriptors ───────────────────────────────────────────────

def _describe_hr(hr: float) -> str:
    if hr > 120:    return "severe tachycardia"
    if hr > 100:    return "elevated heart rate"
    if hr < 50:     return "bradycardia"
    if hr < 60:     return "low heart rate"
    return "normal heart rate"

def _describe_spo2(spo2: float) -> str:
    if spo2 < 88:   return "critical hypoxemia"
    if spo2 < 90:   return "dangerous oxygen drop"
    if spo2 < 94:   return "low SpO2"
    if spo2 < 96:   return "borderline SpO2"
    return "normal SpO2"

def _describe_rr(rr: float) -> str:
    if rr > 30:     return "severe tachypnea"
    if rr > 24:     return "elevated respiratory rate"
    if rr < 10:     return "bradypnea"
    return "normal respiratory rate"

def _describe_bps(bps: float) -> str:
    if bps > 180:   return "hypertensive crisis"
    if bps > 140:   return "high systolic BP"
    if bps < 80:    return "severe hypotension"
    if bps < 90:    return "hypotension"
    return "normal systolic BP"

def _describe_bpd(bpd: float) -> str:
    if bpd > 110:   return "diastolic hypertension"
    if bpd < 50:    return "low diastolic pressure"
    return "normal diastolic BP"
