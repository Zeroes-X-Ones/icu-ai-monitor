"""
anomaly_engine.py
-----------------
Statistical anomaly detection, pattern memory, and patient baseline profiling.

This module operates purely on the patient's own historical vitals, detecting
deviations that are abnormal *relative to that individual* rather than to
population-wide thresholds (which the distress_detector handles).

Key functions:
    detect_anomalies(history)  — Z-score anomaly detection per signal
    detect_patterns(history)   — recurring spike/drop/periodic detection
    build_baseline(history)    — compute patient-specific baseline profile

Design decisions:
    • Z-score thresholds are clinically conservative (|z|>3 → CRITICAL,
      |z|>2 → WARNING) to avoid over-triggering on normal physiological noise.
    • Requires a minimum history window (≥5 readings) before flagging anomalies
      to prevent cold-start false positives.
    • Pattern detection uses a sliding window approach, only marking a signal
      as "recurrent" if the same anomaly class appears >3 times.
"""

from __future__ import annotations

import logging
import math
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# ── Signal key mapping ────────────────────────────────────────────────────────
# Maps internal signal names → dict keys used across the codebase.
_SIGNAL_MAP = {
    "heart_rate":  "heart_rate",
    "spo2":        "spo2",
    "respiratory_rate": "respiratory_rate",
    "bp_systolic": "blood_pressure_systolic",
}

# Friendly display names for output
_SIGNAL_LABELS = {
    "heart_rate":  "Heart Rate",
    "spo2":        "SpO2",
    "respiratory_rate": "Respiratory Rate",
    "bp_systolic": "Blood Pressure (Systolic)",
}

# Minimum number of readings required for meaningful statistics
_MIN_HISTORY = 5

# Z-score thresholds (conservative, clinically appropriate)
_Z_CRITICAL = 3.0
_Z_WARNING  = 2.0

# Minimum standard deviation floor to avoid div-by-zero on perfectly flat data
_MIN_STD = 0.5


# ── Helpers ───────────────────────────────────────────────────────────────────

def _extract_values(history: List[Dict], key: str) -> List[float]:
    """Extract numeric values for a signal from history, skipping None/missing."""
    values = []
    for entry in history:
        v = entry.get(key)
        if v is not None:
            try:
                values.append(float(v))
            except (TypeError, ValueError):
                pass
    return values


def _mean(values: List[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _std(values: List[float], mean_val: float) -> float:
    if len(values) < 2:
        return 0.0
    variance = sum((x - mean_val) ** 2 for x in values) / (len(values) - 1)
    return math.sqrt(variance)


def _z_score(value: float, mean_val: float, std_val: float) -> float:
    """Compute Z-score with a floor on std to prevent division by zero."""
    effective_std = max(std_val, _MIN_STD)
    return (value - mean_val) / effective_std


# ── 1. Anomaly Detection ─────────────────────────────────────────────────────

def detect_anomalies(history: List[Dict]) -> List[Dict]:
    """
    Detect statistical anomalies in the latest vital reading relative to the
    patient's own recent history.

    Parameters
    ----------
    history : list of dict
        Last N vitals readings (oldest → newest). Each dict should contain
        heart_rate, spo2, respiratory_rate, blood_pressure_systolic.

    Returns
    -------
    list of dict
        Each anomaly dict contains:
        {
            "signal": str,          # e.g. "heart_rate"
            "label": str,           # e.g. "Heart Rate"
            "current_value": float,
            "mean": float,
            "std": float,
            "z_score": float,
            "severity": str,        # "WARNING" | "CRITICAL"
            "reason": str,
        }
        Empty list if no anomalies or insufficient data.
    """
    if not history or len(history) < _MIN_HISTORY:
        return []

    anomalies: List[Dict] = []
    latest = history[-1]

    for signal_name, dict_key in _SIGNAL_MAP.items():
        values = _extract_values(history, dict_key)
        if len(values) < _MIN_HISTORY:
            continue

        current = latest.get(dict_key)
        if current is None:
            continue
        current = float(current)

        mean_val = _mean(values)
        std_val  = _std(values, mean_val)
        z = _z_score(current, mean_val, std_val)
        abs_z = abs(z)

        severity = None
        if abs_z > _Z_CRITICAL:
            severity = "CRITICAL"
        elif abs_z > _Z_WARNING:
            severity = "WARNING"

        if severity:
            direction = "above" if z > 0 else "below"
            label = _SIGNAL_LABELS.get(signal_name, signal_name)
            anomalies.append({
                "signal":        signal_name,
                "label":         label,
                "current_value": round(current, 1),
                "mean":          round(mean_val, 2),
                "std":           round(std_val, 2),
                "z_score":       round(z, 2),
                "severity":      severity,
                "reason":        (
                    f"{label} ({round(current, 1)}) is {abs_z:.1f}σ {direction} "
                    f"patient baseline (mean {round(mean_val, 1)}, σ={round(std_val, 1)})"
                ),
            })

    return anomalies


# ── 2. Pattern Detection ─────────────────────────────────────────────────────

def detect_patterns(history: List[Dict]) -> Dict:
    """
    Detect recurring anomaly patterns across the patient's vital-sign history.

    Looks for:
        • Repeated spikes (value significantly above mean)
        • Recurring drops (value significantly below mean)
        • Periodic behavior (consistent intervals between anomalies)

    Parameters
    ----------
    history : list of dict
        Recent vitals window (oldest → newest).

    Returns
    -------
    dict
        {
            "patterns": [
                {
                    "pattern": str,      # e.g. "Recurrent SpO2 drops"
                    "signal": str,
                    "count": int,
                    "confidence": float,  # 0.0–1.0
                    "periodic": bool,
                    "description": str,
                }
            ],
            "has_patterns": bool,
        }
    """
    result: Dict = {"patterns": [], "has_patterns": False}

    if not history or len(history) < _MIN_HISTORY:
        return result

    for signal_name, dict_key in _SIGNAL_MAP.items():
        values = _extract_values(history, dict_key)
        if len(values) < _MIN_HISTORY:
            continue

        mean_val = _mean(values)
        std_val  = _std(values, mean_val)
        effective_std = max(std_val, _MIN_STD)

        # Identify spike and drop indices (|z| > 1.5 — lower bar than anomaly
        # detection because we're looking for recurrence, not single events)
        spike_indices: List[int] = []
        drop_indices: List[int]  = []

        for i, v in enumerate(values):
            z = (v - mean_val) / effective_std
            if z > 1.5:
                spike_indices.append(i)
            elif z < -1.5:
                drop_indices.append(i)

        label = _SIGNAL_LABELS.get(signal_name, signal_name)

        # Check for recurrent spikes (>3 occurrences = pattern)
        if len(spike_indices) > 3:
            periodic, conf = _check_periodicity(spike_indices)
            pattern_conf = min(1.0, len(spike_indices) / len(values) + 0.3)
            if periodic:
                pattern_conf = min(1.0, pattern_conf + 0.2)

            result["patterns"].append({
                "pattern":     f"Recurrent {label} spikes",
                "signal":      signal_name,
                "count":       len(spike_indices),
                "confidence":  round(pattern_conf, 2),
                "periodic":    periodic,
                "description": (
                    f"{label} spiked {len(spike_indices)} times in the observation window"
                    + (" at regular intervals" if periodic else "")
                    + ", suggesting an underlying physiological trigger."
                ),
            })

        # Check for recurrent drops (>3 occurrences = pattern)
        if len(drop_indices) > 3:
            periodic, conf = _check_periodicity(drop_indices)
            pattern_conf = min(1.0, len(drop_indices) / len(values) + 0.3)
            if periodic:
                pattern_conf = min(1.0, pattern_conf + 0.2)

            result["patterns"].append({
                "pattern":     f"Recurrent {label} drops",
                "signal":      signal_name,
                "count":       len(drop_indices),
                "confidence":  round(pattern_conf, 2),
                "periodic":    periodic,
                "description": (
                    f"{label} dropped {len(drop_indices)} times in the observation window"
                    + (" at regular intervals" if periodic else "")
                    + ", suggesting unstable regulation."
                ),
            })

    result["has_patterns"] = len(result["patterns"]) > 0
    return result


def _check_periodicity(indices: List[int], tolerance: float = 0.3) -> tuple:
    """
    Check whether anomaly occurrences happen at roughly regular intervals.

    Parameters
    ----------
    indices   : sorted list of occurrence indices
    tolerance : fraction of mean interval within which we consider intervals "consistent"

    Returns
    -------
    (is_periodic: bool, confidence: float)
    """
    if len(indices) < 3:
        return False, 0.0

    intervals = [indices[i+1] - indices[i] for i in range(len(indices) - 1)]
    mean_interval = _mean(intervals)
    if mean_interval < 1:
        return False, 0.0

    # Count how many intervals fall within tolerance of the mean
    consistent = sum(
        1 for gap in intervals
        if abs(gap - mean_interval) <= mean_interval * tolerance
    )
    ratio = consistent / len(intervals)
    is_periodic = ratio >= 0.6  # 60%+ consistent → periodic

    return is_periodic, round(ratio, 2)


# ── 3. Baseline Profiling ────────────────────────────────────────────────────

def build_baseline(history: List[Dict]) -> Dict:
    """
    Compute a patient-specific baseline profile from historical vitals.

    Parameters
    ----------
    history : list of dict
        All available vitals readings for the patient.

    Returns
    -------
    dict
        {
            "hr_mean":   float,
            "hr_std":    float,
            "spo2_mean": float,
            "spo2_std":  float,
            "rr_mean":   float,
            "rr_std":    float,
            "bp_mean":   float,
            "bp_std":    float,
            "readings_count": int,
            "sufficient_data": bool,
        }
    """
    if not history:
        return _empty_baseline()

    hr_vals  = _extract_values(history, "heart_rate")
    spo2_vals = _extract_values(history, "spo2")
    rr_vals  = _extract_values(history, "respiratory_rate")
    bp_vals  = _extract_values(history, "blood_pressure_systolic")

    sufficient = len(hr_vals) >= _MIN_HISTORY

    hr_mean  = _mean(hr_vals)
    spo2_mean = _mean(spo2_vals)
    rr_mean  = _mean(rr_vals)
    bp_mean  = _mean(bp_vals)

    return {
        "hr_mean":          round(hr_mean, 1),
        "hr_std":           round(_std(hr_vals, hr_mean), 2),
        "spo2_mean":        round(spo2_mean, 1),
        "spo2_std":         round(_std(spo2_vals, spo2_mean), 2),
        "rr_mean":          round(rr_mean, 1),
        "rr_std":           round(_std(rr_vals, rr_mean), 2),
        "bp_mean":          round(bp_mean, 1),
        "bp_std":           round(_std(bp_vals, bp_mean), 2),
        "readings_count":   len(hr_vals),
        "sufficient_data":  sufficient,
    }


def _empty_baseline() -> Dict:
    return {
        "hr_mean": 0, "hr_std": 0,
        "spo2_mean": 0, "spo2_std": 0,
        "rr_mean": 0, "rr_std": 0,
        "bp_mean": 0, "bp_std": 0,
        "readings_count": 0,
        "sufficient_data": False,
    }
