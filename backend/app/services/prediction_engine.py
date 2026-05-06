"""
prediction_engine.py
--------------------
Time-series forecasting engine for ICU vitals.

Predicts future vital signs (10-30 minute window) using linear slope
extrapolation from recent trends. No deep learning -- fully explainable.

Public API
----------
predict_future_vitals(history)  -> dict:
    {
        "forecast": {
            "spo2":       float,
            "heart_rate": float,
            "bp_sys":     float,
            "respiratory_rate": float,
        },
        "risk_prediction": str,
        "confidence":      float,
        "explanation":     str,
    }
"""

from __future__ import annotations

import logging
import math
from typing import Dict, List, Optional

from app.services.trend_analysis import _linear_trend

logger = logging.getLogger(__name__)

# ── Physiological clamps ─────────────────────────────────────────────────────────
# Keeps forecasts within medically realistic ranges.

_CLAMP = {
    "spo2":                    (85.0,  100.0),
    "heart_rate":              (40.0,  160.0),
    "blood_pressure_systolic": (80.0,  200.0),
    "respiratory_rate":        (8.0,   40.0),
}

# ── Forecast multiplier ─────────────────────────────────────────────────────────
# Slope is per-sample.  A 15-min window with ~1 reading/sec would be ~900 samples,
# but our history is usually 10-30 readings.  The multiplier converts the per-sample
# slope into a 10-15 minute forward projection.
_FORECAST_FACTOR = 12  # conservative mid-range (10-15 min)


# ── Noise / consistency measurement ─────────────────────────────────────────────

def _residual_ratio(values: List[float], slope: float) -> float:
    """
    Compute the ratio of the residual variance to the total variance.
    Low ratio = strong linear trend (good confidence).
    High ratio = noisy data (low confidence).
    Returns a value in [0, 1].  0 means perfect trend, 1 means pure noise.
    """
    n = len(values)
    if n < 3:
        return 1.0  # not enough data to judge

    y_mean = sum(values) / n
    total_var = sum((v - y_mean) ** 2 for v in values)
    if total_var == 0:
        return 0.0  # constant signal -- perfectly predictable

    # Predicted values from the linear trend line
    intercept = y_mean - slope * ((n - 1) / 2)
    residual_var = sum((v - (intercept + slope * i)) ** 2 for i, v in enumerate(values))

    return min(residual_var / total_var, 1.0)


def _compute_confidence(slopes: Dict[str, float], residuals: Dict[str, float]) -> float:
    """
    Compute an overall forecast confidence (0-1) based on trend strength
    and data consistency across all signals.

    Strategy:
        - Strong, consistent trend on any signal -> high confidence
        - Weak trends everywhere -> medium confidence (stable prediction is easy)
        - Noisy data -> low confidence

    Returns
    -------
    float in [0, 1]
    """
    # Average residual ratio (lower = cleaner trends)
    avg_residual = sum(residuals.values()) / max(len(residuals), 1)

    # Maximum absolute slope (normalised to meaningful units)
    norm_slopes = {
        "spo2":       abs(slopes.get("spo2", 0)) / 0.1,       # 0.1/sample = rapid
        "heart_rate": abs(slopes.get("heart_rate", 0)) / 0.5,
        "bp_sys":     abs(slopes.get("bp_sys", 0)) / 0.5,
        "rr":         abs(slopes.get("rr", 0)) / 0.3,
    }
    max_norm = max(norm_slopes.values()) if norm_slopes else 0

    # Trend strength bucket
    if max_norm > 1.0:
        trend_base = 0.85
    elif max_norm > 0.4:
        trend_base = 0.70
    elif max_norm > 0.1:
        trend_base = 0.55
    else:
        # Very flat -> stable prediction, moderate-high confidence
        trend_base = 0.65

    # Noise penalty
    noise_penalty = avg_residual * 0.35   # up to 0.35 reduction

    confidence = max(0.15, min(trend_base - noise_penalty, 0.95))
    return round(confidence, 2)


# ── Core forecast function ───────────────────────────────────────────────────────

def predict_future_vitals(history: List[Dict]) -> Dict:
    """
    Forecast vital signs 10-15 minutes into the future using linear
    trend extrapolation from the most recent readings.

    Parameters
    ----------
    history : list of dicts
        Each dict must have at least: heart_rate, spo2.
        Optional: respiratory_rate, blood_pressure_systolic.

    Returns
    -------
    {
        "forecast": {
            "spo2":              float,
            "heart_rate":        float,
            "bp_sys":            float,
            "respiratory_rate":  float,
        },
        "risk_prediction":  str,
        "confidence":       float,
        "explanation":      str,
    }
    """
    # ── Fallback for insufficient data ────────────────────────────────────────
    if not history or len(history) < 3:
        last = history[-1] if history else {}
        return {
            "forecast": {
                "spo2":             last.get("spo2", 97.0),
                "heart_rate":       last.get("heart_rate", 75.0),
                "bp_sys":           last.get("blood_pressure_systolic", 120.0),
                "respiratory_rate": last.get("respiratory_rate", 16.0),
            },
            "risk_prediction": "Insufficient data for trend-based forecast",
            "confidence":      0.2,
            "explanation":     "Fewer than 3 readings available; forecast defaults to last known values.",
        }

    # ── 1. Extract signal arrays ──────────────────────────────────────────────
    hr_vals  = [float(r.get("heart_rate", 75))   for r in history]
    spo2_vals = [float(r.get("spo2", 97))         for r in history]
    bp_vals  = [float(r.get("blood_pressure_systolic", 120)) for r in history]
    rr_vals  = [float(r.get("respiratory_rate", 16) or 16)   for r in history]

    # ── 2. Compute slopes using existing trend_analysis._linear_trend ─────────
    hr_slope   = _linear_trend(hr_vals)
    spo2_slope = _linear_trend(spo2_vals)
    bp_slope   = _linear_trend(bp_vals)
    rr_slope   = _linear_trend(rr_vals)

    slopes = {
        "heart_rate": hr_slope,
        "spo2":       spo2_slope,
        "bp_sys":     bp_slope,
        "rr":         rr_slope,
    }

    # ── 3. Forecast: last_value + slope * factor ──────────────────────────────
    last_hr   = hr_vals[-1]
    last_spo2 = spo2_vals[-1]
    last_bp   = bp_vals[-1]
    last_rr   = rr_vals[-1]

    pred_hr   = last_hr   + (hr_slope   * _FORECAST_FACTOR)
    pred_spo2 = last_spo2 + (spo2_slope * _FORECAST_FACTOR)
    pred_bp   = last_bp   + (bp_slope   * _FORECAST_FACTOR)
    pred_rr   = last_rr   + (rr_slope   * _FORECAST_FACTOR)

    # ── 4. Clamp to physiological limits ──────────────────────────────────────
    pred_hr   = _clamp(pred_hr,   *_CLAMP["heart_rate"])
    pred_spo2 = _clamp(pred_spo2, *_CLAMP["spo2"])
    pred_bp   = _clamp(pred_bp,   *_CLAMP["blood_pressure_systolic"])
    pred_rr   = _clamp(pred_rr,   *_CLAMP["respiratory_rate"])

    forecast = {
        "spo2":             round(pred_spo2, 1),
        "heart_rate":       round(pred_hr, 1),
        "bp_sys":           round(pred_bp, 1),
        "respiratory_rate": round(pred_rr, 1),
    }

    # ── 5. Residuals for confidence ───────────────────────────────────────────
    residuals = {
        "heart_rate": _residual_ratio(hr_vals,   hr_slope),
        "spo2":       _residual_ratio(spo2_vals, spo2_slope),
        "bp_sys":     _residual_ratio(bp_vals,   bp_slope),
        "rr":         _residual_ratio(rr_vals,   rr_slope),
    }

    confidence = _compute_confidence(slopes, residuals)

    # ── 6. Generate risk prediction + explanation ─────────────────────────────
    risk_prediction, explanation = _generate_prediction_summary(
        forecast, slopes, last_hr, last_spo2, last_bp, last_rr
    )

    return {
        "forecast":        forecast,
        "risk_prediction": risk_prediction,
        "confidence":      confidence,
        "explanation":     explanation,
    }


# ── Helpers ──────────────────────────────────────────────────────────────────────

def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def _generate_prediction_summary(
    forecast: Dict,
    slopes: Dict,
    last_hr: float,
    last_spo2: float,
    last_bp: float,
    last_rr: float,
) -> tuple:
    """
    Produce a human-readable risk prediction string and a detailed explanation
    based on forecast values + slope directions.

    Returns (risk_prediction: str, explanation: str)
    """
    risks: List[str] = []
    explanations: List[str] = []

    pred_spo2 = forecast["spo2"]
    pred_hr   = forecast["heart_rate"]
    pred_bp   = forecast["bp_sys"]
    pred_rr   = forecast["respiratory_rate"]

    # -- SpO2 risk --
    if pred_spo2 < 90:
        risks.append("Critical hypoxia risk in next 15 minutes")
        explanations.append(
            f"SpO2 trending from {last_spo2:.1f}% toward {pred_spo2:.1f}% "
            f"(slope: {slopes['spo2']:.4f}/sample) -- immediate oxygen assessment needed."
        )
    elif pred_spo2 < 92:
        risks.append("High risk of hypoxia in next 15 minutes")
        explanations.append(
            f"SpO2 declining from {last_spo2:.1f}% toward {pred_spo2:.1f}% "
            f"(slope: {slopes['spo2']:.4f}/sample)."
        )

    # -- Heart rate risk --
    if pred_hr > 130:
        risks.append("Severe tachycardia expected")
        explanations.append(
            f"Heart rate rising from {last_hr:.0f} toward {pred_hr:.0f} bpm "
            f"(slope: {slopes['heart_rate']:.4f}/sample)."
        )
    elif pred_hr > 110:
        risks.append("Possible tachycardia worsening")
        explanations.append(
            f"Heart rate trending from {last_hr:.0f} toward {pred_hr:.0f} bpm "
            f"(slope: {slopes['heart_rate']:.4f}/sample)."
        )
    elif pred_hr < 50:
        risks.append("Bradycardia risk emerging")
        explanations.append(
            f"Heart rate declining from {last_hr:.0f} toward {pred_hr:.0f} bpm."
        )

    # -- Blood pressure risk --
    if pred_bp > 160:
        risks.append("Hypertensive crisis risk")
        explanations.append(
            f"Systolic BP rising from {last_bp:.0f} toward {pred_bp:.0f} mmHg."
        )
    elif pred_bp > 140:
        risks.append("Hypertension risk")
        explanations.append(
            f"Systolic BP trending from {last_bp:.0f} toward {pred_bp:.0f} mmHg."
        )
    elif pred_bp < 85:
        risks.append("Hypotension risk")
        explanations.append(
            f"Systolic BP declining from {last_bp:.0f} toward {pred_bp:.0f} mmHg."
        )

    # -- Respiratory rate risk --
    if pred_rr > 28:
        risks.append("Tachypnea worsening")
        explanations.append(
            f"Respiratory rate rising from {last_rr:.0f} toward {pred_rr:.0f} br/min."
        )

    # -- Build final strings --
    if not risks:
        risk_prediction = "Vitals expected to remain stable"
        explanation = (
            f"Forecast: HR {pred_hr:.0f}, SpO2 {pred_spo2:.1f}%, "
            f"BP {pred_bp:.0f}, RR {pred_rr:.0f} -- all within safe thresholds."
        )
    else:
        risk_prediction = "; ".join(risks)
        explanation = " ".join(explanations)

    return risk_prediction, explanation
