"""
trend_analysis.py
-----------------
Slope-based per-signal trend analysis with an aggregated overall_trend flag.
"""

from typing import List, Dict


def _linear_trend(values: List[float]) -> float:
    """
    Returns the slope of a simple linear regression over the values.
    Positive → rising, Negative → falling.
    """
    n = len(values)
    if n < 2:
        return 0.0
    x_mean = (n - 1) / 2
    y_mean = sum(values) / n
    numerator = sum((i - x_mean) * (v - y_mean) for i, v in enumerate(values))
    denominator = sum((i - x_mean) ** 2 for i in range(n))
    return numerator / denominator if denominator != 0 else 0.0


def _describe_signal(slope: float, signal: str) -> Dict:
    """Build a per-signal descriptor dict from slope value."""
    abs_slope = abs(slope)

    if signal == "spo2":
        threshold_rapid = 0.05
        threshold_slow  = 0.01
        severe_threshold = 0.15   # SpO₂ dropping fast is critical
    else:
        threshold_rapid  = 0.3
        threshold_slow   = 0.05
        severe_threshold = 1.0

    is_severe = abs_slope > severe_threshold

    if abs_slope < threshold_slow:
        direction = "stable"
        label = f"{signal.replace('_', ' ').title()} is stable"
    elif slope > 0:
        direction = "rising"
        intensity = "rapidly" if abs_slope > threshold_rapid else "slowly"
        label = f"{signal.replace('_', ' ').title()} is {intensity} rising"
    else:
        direction = "falling"
        intensity = "rapidly" if abs_slope > threshold_rapid else "slowly"
        label = f"{signal.replace('_', ' ').title()} is {intensity} falling"

    return {
        "slope":     round(slope, 4),
        "direction": direction,
        "label":     label,
        "is_severe": is_severe,
    }


def analyze_trends(history: list) -> dict:
    """
    Analyse the last N vitals readings and return per-signal trend descriptors
    plus an aggregated overall_trend and alert list.

    Parameters
    ----------
    history : list of dicts with keys: heart_rate, spo2, respiratory_rate

    Returns
    -------
    {
        "heart_rate"       : {slope, direction, label, is_severe},
        "spo2"             : {slope, direction, label, is_severe},
        "respiratory_rate" : {slope, direction, label, is_severe},
        "overall_trend"    : "stable" | "worsening" | "improving",
        "alerts"           : List[str]
    }
    """
    if len(history) < 5:
        return {
            "heart_rate":       {"slope": 0, "direction": "stable", "label": "Insufficient data", "is_severe": False},
            "spo2":             {"slope": 0, "direction": "stable", "label": "Insufficient data", "is_severe": False},
            "respiratory_rate": {"slope": 0, "direction": "stable", "label": "Insufficient data", "is_severe": False},
            "overall_trend":    "stable",
            "alerts":           [],
        }

    hr_vals  = [r["heart_rate"]       for r in history]
    spo2_vals = [r["spo2"]            for r in history]
    rr_vals  = [r["respiratory_rate"] for r in history if r.get("respiratory_rate") is not None]

    hr_slope   = _linear_trend(hr_vals)
    spo2_slope = _linear_trend(spo2_vals)
    rr_slope   = _linear_trend(rr_vals) if rr_vals else 0.0

    hr_info   = _describe_signal(hr_slope,   "heart_rate")
    spo2_info = _describe_signal(spo2_slope, "spo2")
    rr_info   = _describe_signal(rr_slope,   "respiratory_rate")

    # ── Clinical alerts ────────────────────────────────────────────
    alerts = []
    if spo2_slope < -0.05:
        sev = "⚠️ SEVERE" if spo2_info["is_severe"] else "⚠️"
        alerts.append(f"{sev} SpO₂ is declining — monitor closely (slope: {spo2_slope:.4f})")
    if hr_slope > 0.5:
        alerts.append(f"⚠️ Heart rate is rising rapidly (slope: {hr_slope:.4f})")
    if hr_slope < -0.5:
        alerts.append(f"⚠️ Heart rate is falling rapidly — risk of bradycardia (slope: {hr_slope:.4f})")
    if rr_slope > 0.3:
        alerts.append(f"⚠️ Respiratory rate increasing (slope: {rr_slope:.4f})")

    # ── Aggregate overall_trend ────────────────────────────────────
    worsening_signals = 0
    improving_signals = 0

    # HR rising or SpO2 falling = worsening cardiovascular/respiratory state
    if hr_slope > 0.1:
        worsening_signals += 1
    if spo2_slope < -0.01:
        worsening_signals += 2   # SpO2 drop is weighted heavier
    if rr_slope > 0.15:
        worsening_signals += 1

    # HR normalising (falling from high) or SpO2 rising = improving
    if hr_slope < -0.1:
        improving_signals += 1
    if spo2_slope > 0.01:
        improving_signals += 1
    if rr_slope < -0.1:
        improving_signals += 1

    if worsening_signals >= 2:
        overall_trend = "worsening"
    elif improving_signals >= 2:
        overall_trend = "improving"
    else:
        overall_trend = "stable"

    return {
        "heart_rate":       hr_info,
        "spo2":             spo2_info,
        "respiratory_rate": rr_info,
        "overall_trend":    overall_trend,
        "alerts":           alerts,
    }
