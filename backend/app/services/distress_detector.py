"""
distress_detector.py
--------------------
Advanced multi-metric distress scoring engine (0–100 scale).

Score thresholds:
    NORMAL   :  0 – 34
    WARNING  : 35 – 69
    CRITICAL : 70 – 100
"""

from typing import Optional


def calculate_distress(
    heart_rate: float,
    spo2: float,
    respiratory_rate: float,
    bp_sys: Optional[float] = None,
    bp_dia: Optional[float] = None,
    trend: str = "stable",
) -> dict:
    """
    Compute a comprehensive physiological distress score (0–100).

    Parameters
    ----------
    heart_rate        : Current HR in bpm.
    spo2              : Current SpO₂ in %.
    respiratory_rate  : Current RR in breaths/min.
    bp_sys            : Systolic BP in mmHg (optional).
    bp_dia            : Diastolic BP in mmHg (optional).
    trend             : Overall trend string – 'stable' | 'worsening' | 'improving'.

    Returns
    -------
    {
        "distress_score" : int (0-100),
        "risk_level"     : "NORMAL" | "WARNING" | "CRITICAL",
        "reasons"        : List[str],
        "correlation_flags": List[str]   # multi-metric cross-signal alerts
    }
    """
    score = 0
    reasons = []
    correlation_flags = []

    # ──────────────────────────────────────────
    # 1. SpO₂  (highest clinical priority)
    # ──────────────────────────────────────────
    if spo2 < 88:
        score += 45
        reasons.append(f"Severe hypoxemia — SpO₂ critically low at {round(spo2, 1)}%")
    elif spo2 < 90:
        score += 40
        reasons.append(f"Dangerous oxygen drop — SpO₂ at {round(spo2, 1)}%")
    elif spo2 < 94:
        score += 25
        reasons.append(f"Low oxygen saturation — SpO₂ at {round(spo2, 1)}%")
    elif spo2 < 96:
        score += 10
        reasons.append(f"Borderline SpO₂ at {round(spo2, 1)}%")

    # ──────────────────────────────────────────
    # 2. Heart Rate
    # ──────────────────────────────────────────
    if heart_rate > 130:
        score += 28
        reasons.append(f"Severe tachycardia — HR at {round(heart_rate)} bpm")
    elif heart_rate > 120:
        score += 22
        reasons.append(f"Tachycardia — HR at {round(heart_rate)} bpm")
    elif heart_rate > 100:
        score += 14
        reasons.append(f"Elevated HR at {round(heart_rate)} bpm")
    elif heart_rate < 45:
        score += 30
        reasons.append(f"Severe bradycardia — HR at {round(heart_rate)} bpm")
    elif heart_rate < 55:
        score += 20
        reasons.append(f"Bradycardia — HR at {round(heart_rate)} bpm")
    elif heart_rate < 60:
        score += 10
        reasons.append(f"Low-normal HR at {round(heart_rate)} bpm")

    # ──────────────────────────────────────────
    # 3. Respiratory Rate
    # ──────────────────────────────────────────
    if respiratory_rate > 30:
        score += 22
        reasons.append(f"Severe tachypnea — RR at {round(respiratory_rate)} br/min")
    elif respiratory_rate > 24:
        score += 14
        reasons.append(f"Elevated respiratory rate at {round(respiratory_rate)} br/min")
    elif respiratory_rate > 20:
        score += 6
        reasons.append(f"Mildly elevated RR at {round(respiratory_rate)} br/min")
    elif respiratory_rate < 10:
        score += 20
        reasons.append(f"Bradypnea — RR at {round(respiratory_rate)} br/min")

    # ──────────────────────────────────────────
    # 4. Blood Pressure
    # ──────────────────────────────────────────
    if bp_sys is not None:
        if bp_sys > 180:
            score += 20
            reasons.append(f"Hypertensive crisis — Systolic at {round(bp_sys)} mmHg")
        elif bp_sys > 160:
            score += 15
            reasons.append(f"Stage 2 hypertension — Systolic at {round(bp_sys)} mmHg")
        elif bp_sys > 140:
            score += 10
            reasons.append(f"Elevated systolic BP at {round(bp_sys)} mmHg")
        elif bp_sys < 80:
            score += 25
            reasons.append(f"Severe hypotension — Systolic at {round(bp_sys)} mmHg")
        elif bp_sys < 90:
            score += 18
            reasons.append(f"Hypotension — Systolic at {round(bp_sys)} mmHg")

    if bp_dia is not None:
        if bp_dia > 110:
            score += 12
            reasons.append(f"Diastolic hypertension — {round(bp_dia)} mmHg")
        elif bp_dia < 50:
            score += 10
            reasons.append(f"Low diastolic pressure — {round(bp_dia)} mmHg")

    # ──────────────────────────────────────────
    # 5. Multi-metric correlation bonuses
    # ──────────────────────────────────────────
    if heart_rate > 100 and spo2 < 94:
        bonus = 15
        score += bonus
        correlation_flags.append(
            f"⚠ Concurrent tachycardia ({round(heart_rate)} bpm) & hypoxemia ({round(spo2, 1)}%) — "
            "suggests respiratory distress or pulmonary embolism"
        )

    if bp_sys is not None and bp_sys < 90 and heart_rate > 100:
        bonus = 18
        score += bonus
        correlation_flags.append(
            f"🔴 Hypotension ({round(bp_sys)} mmHg) + tachycardia ({round(heart_rate)} bpm) — "
            "shock pattern detected (hypovolemic/septic)"
        )

    if respiratory_rate > 24 and spo2 < 94:
        bonus = 10
        score += bonus
        correlation_flags.append(
            f"⚠ High RR ({round(respiratory_rate)} br/min) + low SpO₂ ({round(spo2, 1)}%) — "
            "active respiratory compromise"
        )

    # ──────────────────────────────────────────
    # 6. Trend modifier
    # ──────────────────────────────────────────
    if trend == "worsening":
        score += 15
        reasons.append("Overall patient trend is worsening")
    elif trend == "improving":
        score = max(0, score - 10)
        reasons.append("Overall patient trend is improving")

    # ──────────────────────────────────────────
    # 7. Clamp & classify
    # ──────────────────────────────────────────
    score = max(0, min(score, 100))

    if score >= 70:
        risk_level = "CRITICAL"
    elif score >= 35:
        risk_level = "WARNING"
    else:
        risk_level = "NORMAL"

    return {
        "distress_score": score,
        "risk_level": risk_level,
        "reasons": reasons,
        "correlation_flags": correlation_flags,
    }