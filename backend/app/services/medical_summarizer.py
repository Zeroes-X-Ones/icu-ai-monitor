"""
medical_summarizer.py
---------------------
Generates a rich, structured clinical summary from a window of vitals history.

Input:
    history : list of dicts (oldest→newest), each with keys:
              heart_rate, spo2, respiratory_rate, blood_pressure_systolic,
              blood_pressure_diastolic
    latest  : dict — the most recent vital-sign snapshot (same schema)

Output dict:
    summary            : str  — narrative paragraph
    distress           : dict — distress_score, risk_level, reasons, correlation_flags
    trends             : dict — per-signal trend analysis + overall_trend
    possible_condition : str
    prediction         : str
    recommendation     : str
    snapshot           : dict — current HR, SpO2, RR
"""

from app.services.distress_detector import calculate_distress
from app.services.trend_analysis    import analyze_trends

# -- Safe import of anomaly engine (never crashes this module) -----------------
try:
    from app.services.anomaly_engine import detect_anomalies, detect_patterns, build_baseline
    _ANOMALY_AVAILABLE = True
except ImportError:
    _ANOMALY_AVAILABLE = False

    def detect_anomalies(history):  # type: ignore
        return []

    def detect_patterns(history):  # type: ignore
        return {"patterns": [], "has_patterns": False}

    def build_baseline(history):  # type: ignore
        return {"hr_mean": 0, "spo2_mean": 0, "rr_mean": 0, "bp_mean": 0,
                "readings_count": 0, "sufficient_data": False}


# ── Condition inference ────────────────────────────────────────────────────────

_CONDITION_RULES = [
    # (check_fn, condition_name)
    (lambda h, s, r, bp, fl: "respiratory distress" in " ".join(fl).lower(),
     "Acute Respiratory Distress"),
    (lambda h, s, r, bp, fl: "shock" in " ".join(fl).lower(),
     "Hemodynamic Instability / Shock"),
    (lambda h, s, r, bp, fl: s < 90,
     "Severe Hypoxemia"),
    (lambda h, s, r, bp, fl: h > 120 and s < 94,
     "Respiratory Failure / Pulmonary Embolism (possible)"),
    (lambda h, s, r, bp, fl: bp < 90 and h > 100,
     "Hypovolemic or Septic Shock (possible)"),
    (lambda h, s, r, bp, fl: h > 100 and s >= 94,
     "Tachycardia (isolated)"),
    (lambda h, s, r, bp, fl: h < 55,
     "Bradycardia"),
    (lambda h, s, r, bp, fl: r > 24,
     "Tachypnea / Increased Work of Breathing"),
    (lambda h, s, r, bp, fl: bp > 160,
     "Hypertensive Episode"),
]


def _infer_condition(hr, spo2, rr, bps, correlation_flags) -> str:
    for check, name in _CONDITION_RULES:
        try:
            if check(hr, spo2, rr, bps, correlation_flags):
                return name
        except Exception:
            pass
    return "No acute condition identified"


def _predict(risk_level: str, overall_trend: str, score: int) -> str:
    """Generate a 30-minute prediction string."""
    if risk_level == "CRITICAL":
        if overall_trend == "worsening":
            return (
                "High probability of continued deterioration over the next 30 minutes. "
                "Without intervention, risk of organ compromise or cardiovascular collapse."
            )
        return (
            "Condition is critical but may stabilise with targeted intervention. "
            "Reassess every 5–10 minutes."
        )
    if risk_level == "WARNING":
        if overall_trend == "worsening":
            return (
                "Current trends suggest possible escalation to CRITICAL within 30 minutes "
                "if no corrective action is taken."
            )
        if overall_trend == "improving":
            return "Patient appears to be responding; stable or improved status expected within 30 minutes."
        return "Stable or mild deterioration expected within 30 minutes. Monitor closely."

    if overall_trend == "worsening":
        return "Vital signs are currently normal but trending unfavourably. Reassess within 15 minutes."
    return "Patient is expected to remain stable over the next 30 minutes if current trends persist."


def _build_narrative(
    hr, spo2, rr, bps,
    first, hr_delta, spo2_delta, rr_delta,
    distress, trends,
    anomalies=None, patterns=None,
) -> str:
    """Assemble a concise clinical narrative paragraph."""
    lines: list[str] = []

    # HR
    if abs(hr_delta) >= 2:
        direction = "increased" if hr_delta > 0 else "decreased"
        lines.append(
            f"Heart rate has {direction} from {round(first['heart_rate'])} "
            f"to {round(hr)} bpm ({'+' if hr_delta > 0 else ''}{round(hr_delta, 1)} bpm)."
        )
    else:
        lines.append(f"Heart rate is stable at {round(hr)} bpm.")

    # SpO2
    if spo2 < 90:
        lines.append(f"Oxygen saturation is critically low at {round(spo2, 1)}%, requiring urgent attention.")
    elif spo2 < 94:
        lines.append(f"Oxygen saturation has dropped to {round(spo2, 1)}%, below the safe threshold of 94%.")
    elif spo2_delta <= -1:
        lines.append(f"Oxygen saturation has declined to {round(spo2, 1)}% (Δ {round(spo2_delta, 1)}%).")
    else:
        lines.append(f"Oxygen saturation is {round(spo2, 1)}%, within acceptable range.")

    # RR
    if rr > 24:
        lines.append(
            f"Respiratory rate is elevated at {round(rr)} br/min, "
            "indicating increased work of breathing."
        )
    elif abs(rr_delta) >= 2:
        direction = "risen" if rr_delta > 0 else "decreased"
        lines.append(f"Respiratory rate has {direction} to {round(rr)} br/min.")
    else:
        lines.append(f"Respiratory rate is {round(rr)} br/min.")

    # BP
    if bps > 140:
        lines.append(f"Systolic blood pressure is elevated at {round(bps)} mmHg.")
    elif bps < 90:
        lines.append(f"Systolic blood pressure is low at {round(bps)} mmHg — monitor haemodynamics.")

    # Trend alerts
    for alert in trends.get("alerts", []):
        lines.append(alert)

    # Correlation flags
    for flag in distress.get("correlation_flags", []):
        lines.append(flag)

    # Clinical impression
    risk = distress["risk_level"]
    if risk == "CRITICAL":
        lines.append(
            "⚠️ CLINICAL IMPRESSION: Patient is in significant physiological distress. "
            "Immediate clinical escalation is required."
        )
    elif risk == "WARNING":
        lines.append(
            "⚠️ CLINICAL IMPRESSION: Early signs of cardiovascular or respiratory stress detected. "
            "Increase monitoring frequency."
        )
    else:
        lines.append(
            "✅ CLINICAL IMPRESSION: Vitals are within acceptable ranges. Continue routine monitoring."
        )

    # ── Anomaly context ─────────────────────────────────────────────
    if anomalies:
        for anom in anomalies[:2]:  # Keep narrative concise
            direction = "above" if anom.get("z_score", 0) > 0 else "below"
            lines.append(
                f"⚡ ANOMALY: {anom['label']} is {abs(anom.get('z_score', 0)):.1f}σ "
                f"{direction} patient baseline — {anom['severity']} level deviation."
            )

    # ── Pattern context ─────────────────────────────────────────────
    if patterns and patterns.get("has_patterns"):
        for pat in patterns.get("patterns", [])[:2]:
            desc = pat.get("description", pat.get("pattern", ""))
            lines.append(f"🔄 PATTERN: {desc}")

    return " ".join(lines)


# ── Public API ─────────────────────────────────────────────────────────────────


def _generate_hr_summary(history: list, latest: dict, distress: dict, trends: dict) -> dict:
    """Heart-rate-only focused summary."""
    hr  = latest["heart_rate"]
    first = history[0]
    hr_delta = round(hr - first["heart_rate"], 1)
    hr_trend = trends.get("heart_rate", {}).get("direction", "stable")
    risk = distress["risk_level"]

    # Narrative
    if hr > 130:
        narrative = (
            f"Heart rate is critically elevated at {round(hr)} bpm "
            f"({'rising' if hr_delta > 0 else 'from'} {round(first['heart_rate'])} bpm), "
            "indicating severe tachycardia that requires immediate attention."
        )
        cause = "Possible causes: fever, sepsis, pain, hypovolemia, or arrhythmia."
        prediction = "High risk of haemodynamic compromise if tachycardia persists without intervention."
    elif hr > 100:
        narrative = (
            f"Heart rate is elevated at {round(hr)} bpm (Δ {'+' if hr_delta > 0 else ''}{hr_delta} bpm), "
            f"trending {hr_trend}. Consistent with tachycardia."
        )
        cause = "Tachycardia may reflect pain, agitation, fever, or early hypovolemia."
        prediction = (
            "If rising trend continues, HR may worsen over the next 15–30 minutes. "
            "Reassess precipitating factors."
        )
    elif hr < 45:
        narrative = (
            f"Heart rate is dangerously low at {round(hr)} bpm "
            f"(Δ {'+' if hr_delta > 0 else ''}{hr_delta} bpm), indicating severe bradycardia."
        )
        cause = "Severe bradycardia may indicate heart block, medication toxicity, or vasovagal response."
        prediction = "Risk of cardiac arrest or haemodynamic collapse if HR declines further."
    elif hr < 55:
        narrative = (
            f"Heart rate is low at {round(hr)} bpm (Δ {'+' if hr_delta > 0 else ''}{hr_delta} bpm). "
            f"Trend: {hr_trend}."
        )
        cause = "Bradycardia may be medication-related, vagal, or indicate conduction abnormality."
        prediction = "Patient may become symptomatic if heart rate drops further. Monitor closely."
    elif abs(hr_delta) >= 5:
        direction = "increased" if hr_delta > 0 else "decreased"
        narrative = (
            f"Heart rate has {direction} from {round(first['heart_rate'])} to {round(hr)} bpm "
            f"({'+' if hr_delta > 0 else ''}{hr_delta} bpm), currently trending {hr_trend}."
        )
        cause = "Dynamic HR change may reflect physiological stress, activity, or medication effect."
        prediction = (
            f"Heart rate is {hr_trend} — continued monitoring recommended to confirm stabilisation."
        )
    else:
        narrative = f"Heart rate is stable at {round(hr)} bpm. No acute cardiac concern identified."
        cause = "Normal sinus rhythm with no significant HR deviation."
        prediction = "Heart rate expected to remain stable over the next 30 minutes."

    return {
        "key_observation": narrative[:150] + "..." if len(narrative) > 150 else narrative,
        "possible_cause": cause,
        "prediction": prediction,
        "recommendation_summary": "Cardiac monitoring advised" if risk != "NORMAL" else "Routine monitoring",
        "risk_reason": narrative,
        "summary": narrative,
        "distress": distress,
        "trends": trends,
        "possible_condition": "Tachycardia" if hr > 100 else "Bradycardia" if hr < 55 else "Normal Sinus Rhythm",
        "snapshot": {"heart_rate": round(hr)},
        "anomalies": [], "anomaly_explanation": "",
        "patterns": {"patterns": [], "has_patterns": False}, "pattern_explanation": "",
        "baseline": {},
    }


def _generate_spo2_summary(history: list, latest: dict, distress: dict, trends: dict) -> dict:
    """SpO2-only focused summary."""
    spo2 = latest["spo2"]
    first = history[0]
    spo2_delta = round(spo2 - first["spo2"], 1)
    spo2_trend = trends.get("spo2", {}).get("direction", "stable")
    risk = distress["risk_level"]

    if spo2 < 88:
        narrative = (
            f"Oxygen saturation is critically low at {round(spo2, 1)}% "
            f"(Δ {'+' if spo2_delta > 0 else ''}{spo2_delta}%), "
            "constituting severe hypoxemia requiring emergency intervention."
        )
        cause = "Severe hypoxemia: possible respiratory failure, PE, or severe pneumonia."
        prediction = "Without immediate O₂ therapy or ventilatory support, risk of hypoxic organ damage is high."
    elif spo2 < 90:
        narrative = (
            f"Oxygen saturation is dangerously low at {round(spo2, 1)}% "
            f"(Δ {spo2_delta}%), trending {spo2_trend}. Significant hypoxia is present."
        )
        cause = "Hypoxia may reflect respiratory distress, V/Q mismatch, or airway compromise."
        prediction = "Escalation of oxygen support is likely required if saturation continues to fall."
    elif spo2 < 94:
        narrative = (
            f"Oxygen saturation has dropped to {round(spo2, 1)}% (Δ {spo2_delta}%), "
            f"below the safe threshold of 94%, and is trending {spo2_trend}."
        )
        cause = "Borderline hypoxia may indicate early respiratory insufficiency or fluid overload."
        prediction = "If trend continues downward, supplemental oxygen or escalation may be needed within 15–20 minutes."
    elif spo2_delta <= -1.5:
        narrative = (
            f"Oxygen saturation has declined from {round(first['spo2'], 1)}% to {round(spo2, 1)}% "
            f"(Δ {spo2_delta}%), trending {spo2_trend}. Requires close observation."
        )
        cause = "Declining SpO₂ trend may reflect evolving respiratory compromise or positioning effect."
        prediction = "Saturation may reach clinical threshold if decline continues. Reassess within 10 minutes."
    else:
        narrative = (
            f"Oxygen saturation is {round(spo2, 1)}%, within acceptable limits. "
            f"Trend is {spo2_trend} with a delta of {'+' if spo2_delta > 0 else ''}{spo2_delta}%."
        )
        cause = "Adequate oxygenation — no current respiratory concern."
        prediction = "SpO₂ is expected to remain within safe range over the next 30 minutes."

    condition = "Severe Hypoxemia" if spo2 < 88 else "Hypoxemia" if spo2 < 94 else "Adequate Oxygenation"
    return {
        "key_observation": narrative[:150] + "..." if len(narrative) > 150 else narrative,
        "possible_cause": cause,
        "prediction": prediction,
        "recommendation_summary": "O₂ therapy indicated" if risk != "NORMAL" else "Routine monitoring",
        "risk_reason": narrative,
        "summary": narrative,
        "distress": distress,
        "trends": trends,
        "possible_condition": condition,
        "snapshot": {"spo2": round(spo2, 1)},
        "anomalies": [], "anomaly_explanation": "",
        "patterns": {"patterns": [], "has_patterns": False}, "pattern_explanation": "",
        "baseline": {},
    }


def _generate_bp_summary(history: list, latest: dict, distress: dict, trends: dict) -> dict:
    """Blood-pressure-only focused summary."""
    bps  = latest.get("blood_pressure_systolic") or 120
    bpd  = latest.get("blood_pressure_diastolic") or 80
    first = history[0]
    bps_delta = round(bps - (first.get("blood_pressure_systolic") or bps), 1)
    bp_trend  = trends.get("heart_rate", {}).get("direction", "stable")  # no direct bp trend; use overall
    overall   = trends.get("overall_trend", "stable")
    risk = distress["risk_level"]

    if bps > 180:
        narrative = (
            f"Blood pressure is in hypertensive crisis at {round(bps)}/{round(bpd)} mmHg "
            f"(Δ systolic {'+' if bps_delta >= 0 else ''}{bps_delta} mmHg). Urgent intervention required."
        )
        cause = "Hypertensive crisis may indicate end-organ damage risk (cerebral, cardiac, renal)."
        prediction = "Without antihypertensive intervention, risk of acute end-organ damage is high."
    elif bps > 160:
        narrative = (
            f"Blood pressure is significantly elevated at {round(bps)}/{round(bpd)} mmHg "
            f"(Δ {'+' if bps_delta >= 0 else ''}{bps_delta} mmHg), consistent with Stage 2 hypertension."
        )
        cause = "Stage 2 hypertension — possible pain response, medication non-compliance, or essential hypertension."
        prediction = "BP is likely to remain elevated without targeted intervention. Reassess within 15 minutes."
    elif bps > 140:
        narrative = (
            f"Blood pressure is elevated at {round(bps)}/{round(bpd)} mmHg "
            f"(Δ systolic {'+' if bps_delta >= 0 else ''}{bps_delta} mmHg), indicating hypertension."
        )
        cause = "Hypertension may reflect physiological stress, pain, or pre-existing condition."
        prediction = "Continued monitoring required to determine if BP escalates further."
    elif bps < 80:
        narrative = (
            f"Blood pressure is critically low at {round(bps)}/{round(bpd)} mmHg "
            f"(Δ {'+' if bps_delta >= 0 else ''}{bps_delta} mmHg). Haemodynamic emergency."
        )
        cause = "Severe hypotension may indicate haemorrhage, septic shock, or cardiogenic shock."
        prediction = "Without immediate haemodynamic support, risk of cardiovascular collapse is significant."
    elif bps < 90:
        narrative = (
            f"Blood pressure is low at {round(bps)}/{round(bpd)} mmHg "
            f"(Δ {'+' if bps_delta >= 0 else ''}{bps_delta} mmHg). Hypotension present."
        )
        cause = "Hypotension may reflect hypovolaemia, medication effect, or early shock."
        prediction = "If hypotension persists or deepens, haemodynamic instability is likely within 30 minutes."
    else:
        narrative = (
            f"Blood pressure is {round(bps)}/{round(bpd)} mmHg, within normal limits "
            f"(Δ systolic {'+' if bps_delta >= 0 else ''}{bps_delta} mmHg). Trend: {overall}."
        )
        cause = "Stable haemodynamics — no acute BP concern."
        prediction = "Blood pressure expected to remain stable over the next 30 minutes."

    condition = (
        "Hypertensive Crisis" if bps > 180
        else "Stage 2 Hypertension" if bps > 160
        else "Hypertension" if bps > 140
        else "Severe Hypotension" if bps < 80
        else "Hypotension" if bps < 90
        else "Normotension"
    )
    return {
        "key_observation": narrative[:150] + "..." if len(narrative) > 150 else narrative,
        "possible_cause": cause,
        "prediction": prediction,
        "recommendation_summary": "BP management indicated" if risk != "NORMAL" else "Routine monitoring",
        "risk_reason": narrative,
        "summary": narrative,
        "distress": distress,
        "trends": trends,
        "possible_condition": condition,
        "snapshot": {"blood_pressure_systolic": round(bps), "blood_pressure_diastolic": round(bpd)},
        "anomalies": [], "anomaly_explanation": "",
        "patterns": {"patterns": [], "has_patterns": False}, "pattern_explanation": "",
        "baseline": {},
    }

def generate_summary(history: list, latest: dict, metric: str = None) -> dict:
    """
    Generate structured clinical insights, optionally scoped to a single metric.

    Parameters
    ----------
    history : list of vitals dicts (oldest → newest)
    latest  : most recent vitals dict
    metric  : None (combined) | "heart_rate" | "spo2" | "bp"
    """
    if not latest or len(history) < 2:
        return {
            "key_observation": "Insufficient data collected.",
            "possible_cause": "N/A",
            "prediction": "Awaiting more data.",
            "recommendation_summary": "Continue monitoring.",
            "risk_reason": "No data",
            "summary": "Insufficient data collected. Monitoring in progress…",
            "distress": {"distress_score": 0, "risk_level": "NORMAL", "reasons": [], "correlation_flags": []},
            "trends": {"overall_trend": "stable", "alerts": []}
        }

    hr  = latest["heart_rate"]
    sp  = latest["spo2"]
    rr  = latest.get("respiratory_rate") or 16.0
    bps = latest.get("blood_pressure_systolic") or 120
    bpd = latest.get("blood_pressure_diastolic") or 80

    trends  = analyze_trends(history)
    overall = trends.get("overall_trend", "stable")

    distress = calculate_distress(
        heart_rate=hr,
        spo2=sp,
        respiratory_rate=rr,
        bp_sys=bps,
        bp_dia=bpd,
        trend=overall,
    )

    c_flags = distress.get("correlation_flags", [])

    # ── Metric-specific routing ───────────────────────────────────────
    if metric == "heart_rate":
        return _generate_hr_summary(history, latest, distress, trends)
    elif metric == "spo2":
        return _generate_spo2_summary(history, latest, distress, trends)
    elif metric == "bp":
        return _generate_bp_summary(history, latest, distress, trends)
    # else: combined (dashboard) path continues below

    # ── Anomaly engine (Phase 5) ──────────────────────────────────────
    try:
        anomalies = detect_anomalies(history)
        patterns  = detect_patterns(history)
        baseline  = build_baseline(history)
    except Exception:
        anomalies = []
        patterns  = {"patterns": [], "has_patterns": False}
        baseline  = {"hr_mean": 0, "spo2_mean": 0, "rr_mean": 0, "bp_mean": 0,
                     "readings_count": 0, "sufficient_data": False}

    # Deltas vs first reading in window
    first      = history[0]
    hr_delta   = round(hr - first["heart_rate"],  1)
    spo2_delta = round(sp - first["spo2"],        1)
    rr_delta   = round(rr - (first.get("respiratory_rate") or rr), 1)

    narrative = _build_narrative(hr, sp, rr, bps, first, hr_delta, spo2_delta, rr_delta, distress, trends,
                                 anomalies=anomalies, patterns=patterns)
    condition = _infer_condition(hr, sp, rr, bps, c_flags)
    prediction = _predict(distress["risk_level"], overall, distress["distress_score"])

    # ── Anomaly explanation (human-readable context) ───────────────
    anomaly_explanation = ""
    if anomalies:
        parts = []
        for a in anomalies[:3]:
            parts.append(a.get("reason", ""))
        anomaly_explanation = "; ".join(parts)

    pattern_explanation = ""
    if patterns.get("has_patterns"):
        parts = []
        for p in patterns.get("patterns", [])[:2]:
            parts.append(p.get("description", p.get("pattern", "")))
        pattern_explanation = "; ".join(parts)

    # Build risk_reason
    risk_reason = "Vitals are stable."
    if distress["reasons"]:
        risk_reason = distress["reasons"][0]
    if c_flags:
        risk_reason = c_flags[0]

    # Structured Output for Phase 2
    return {
        "key_observation": narrative[:150] + "..." if len(narrative) > 150 else narrative,
        "possible_cause": condition,
        "prediction": prediction,
        "recommendation_summary": "Clinical review recommended" if distress["risk_level"] != "NORMAL" else "Routine monitoring",
        "risk_reason": risk_reason,
        "summary": narrative, # Keep for backward compatibility
        "distress": distress,
        "trends": trends,
        "possible_condition": condition, # Keep for backward compatibility
        "snapshot": {
            "heart_rate": round(hr),
            "spo2": round(sp, 1),
            "respiratory_rate": round(rr),
            "blood_pressure_systolic": round(bps),
        },
        # -- Phase 5 anomaly intelligence --
        "anomalies":            anomalies,
        "anomaly_explanation":  anomaly_explanation,
        "patterns":             patterns,
        "pattern_explanation":  pattern_explanation,
        "baseline":             baseline,
    }
