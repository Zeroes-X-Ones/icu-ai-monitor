"""
vitals_service.py
-----------------
Database operations for PatientVitals + the deep get_analysis() orchestrator.

get_analysis() pipeline:
    1. Fetch current + previous window vitals from DB
    2. Run trend_analysis  (slope-based per-signal + overall_trend)
    3. Run distress_detector  (on the latest vital)
    4. Run intelligence_service.detect_events()
    5. Generate recommendations, timeline, alert_explanation
    6. Build key_observation, possible_cause, prediction, confidence_score
"""

from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from typing import Optional

from app.models.vitals  import PatientVitals, Alert
from app.schemas.vitals_schema import VitalsCreate
from app.services.ai_engine           import AIEngine
from app.services.distress_detector   import calculate_distress
from app.services.trend_analysis      import analyze_trends
from app.services.intelligence_service import IntelligenceService
from app.services.medical_summarizer import generate_summary


# ── helpers ────────────────────────────────────────────────────────────────────

def _avg(arr):  return round(sum(arr) / len(arr), 1) if arr else 0
def _min(arr):  return round(min(arr), 1) if arr else 0
def _max(arr):  return round(max(arr), 1) if arr else 0


def _to_dict(v: PatientVitals) -> dict:
    """Convert DB model → plain dict for service functions."""
    return {
        "heart_rate":              v.heart_rate,
        "spo2":                    v.spo2,
        "respiratory_rate":        v.respiratory_rate or 16.0,
        "blood_pressure_systolic": v.blood_pressure_systolic,
        "blood_pressure_diastolic": v.blood_pressure_diastolic,
        "alert_level":             v.alert_level,
        "timestamp":               v.timestamp.isoformat(),
    }


def _get_trend_delta(c_avg, p_avg, threshold) -> str:
    if not p_avg:
        return "stable"
    if c_avg - p_avg > threshold:
        return "increasing"
    if c_avg - p_avg < -threshold:
        return "decreasing"
    return "stable"


# ── VitalsService ──────────────────────────────────────────────────────────────

class VitalsService:

    @staticmethod
    def get_session_start(db: Session):
        first = db.query(PatientVitals).order_by(PatientVitals.timestamp.asc()).first()
        return first.timestamp if first else None

    # ── CREATE ─────────────────────────────────────────────────────────────────
    @staticmethod
    def create_vital(db: Session, vitals: VitalsCreate):
        alert_level, ai_summary = AIEngine.analyze_realtime(vitals)

        now = datetime.now(timezone.utc)
        db_vital = PatientVitals(
            heart_rate=vitals.heart_rate,
            spo2=vitals.spo2,
            blood_pressure_systolic=vitals.blood_pressure_systolic,
            blood_pressure_diastolic=vitals.blood_pressure_diastolic,
            respiratory_rate=vitals.respiratory_rate,
            alert_level=alert_level,
            ai_summary=ai_summary,
            timestamp=now,
        )
        db.add(db_vital)
        db.flush()

        # ── Alert generation (distress-aware) ─────────────────────
        hr  = vitals.heart_rate
        sp  = vitals.spo2
        rr  = vitals.respiratory_rate or 16.0
        bps = vitals.blood_pressure_systolic
        bpd = vitals.blood_pressure_diastolic

        distress = calculate_distress(hr, sp, rr, bp_sys=bps, bp_dia=bpd)
        sev_from_score = distress["risk_level"]   # NORMAL | WARNING | CRITICAL

        def alert_sev(value_crit: bool) -> str:
            if sev_from_score == "CRITICAL" or value_crit:
                return "CRITICAL"
            return "WARNING"

        if hr > 100:
            db.add(Alert(
                timestamp=now, vital_type="HR", value=hr,
                severity=alert_sev(hr > 120), reason="High Heart Rate", vitals_id=db_vital.id,
            ))
        elif hr < 55:
            db.add(Alert(
                timestamp=now, vital_type="HR", value=hr,
                severity=alert_sev(hr < 45), reason="Bradycardia", vitals_id=db_vital.id,
            ))

        if sp < 95:
            db.add(Alert(
                timestamp=now, vital_type="SpO2", value=sp,
                severity=alert_sev(sp < 90), reason="Low Oxygen Saturation", vitals_id=db_vital.id,
            ))

        if bps > 140 or bpd > 90:
            db.add(Alert(
                timestamp=now, vital_type="BP", value=bps,
                severity=alert_sev(bps > 160), reason="Elevated Blood Pressure", vitals_id=db_vital.id,
            ))
        elif bps < 90 or bpd < 55:
            db.add(Alert(
                timestamp=now, vital_type="BP", value=bps,
                severity=alert_sev(bps < 80), reason="Hypotension", vitals_id=db_vital.id,
            ))

        db.commit()
        db.refresh(db_vital)
        return db_vital

    # ── READ (history) ─────────────────────────────────────────────────────────
    @staticmethod
    def get_vitals(db: Session, limit: int = 100, minutes: Optional[int] = None):
        query = db.query(PatientVitals)
        if minutes:
            since = datetime.now(timezone.utc) - timedelta(minutes=minutes)
            query = query.filter(PatientVitals.timestamp >= since)
            return query.order_by(PatientVitals.timestamp.asc()).all()
        return query.order_by(PatientVitals.timestamp.desc()).limit(limit).all()

    # ── READ (alerts) ──────────────────────────────────────────────────────────
    @staticmethod
    def get_alerts(db: Session, limit: int = 50):
        return db.query(Alert).order_by(Alert.timestamp.desc()).limit(limit).all()

    # ── DEEP ANALYSIS ─────────────────────────────────────────────────────────
    @staticmethod
    def get_analysis(db: Session, window_minutes: int, metric: Optional[str] = None) -> dict:
        """
        Orchestrated clinical intelligence pipeline (Phase 2 Upgraded).
        """
        now = datetime.now(timezone.utc)
        current_window_start = now - timedelta(minutes=window_minutes)
        prev_window_start    = current_window_start - timedelta(minutes=window_minutes)

        # ── 1. Fetch vitals ────────────────────────────────────────
        curr_vitals = (
            db.query(PatientVitals)
            .filter(PatientVitals.timestamp >= current_window_start)
            .order_by(PatientVitals.timestamp.asc())
            .all()
        )
        prev_vitals = (
            db.query(PatientVitals)
            .filter(
                PatientVitals.timestamp >= prev_window_start,
                PatientVitals.timestamp <  current_window_start,
            )
            .order_by(PatientVitals.timestamp.asc())
            .all()
        )

        # Base confidence from data volume
        expected_readings = window_minutes * 12 # Assume 1 reading every 5s approx
        volume_score = min(1.0, len(curr_vitals) / expected_readings) if expected_readings > 0 else 0.0

        empty_metric = {"avg": 0, "min": 0, "max": 0, "abnormal_frequency": 0, "trend": "stable", "spikes_drops": 0}

        if not curr_vitals or len(curr_vitals) < 5:
            return {
                "window_minutes":   window_minutes,
                "key_observation":  "Insufficient data available.",
                "risk_level":       "NORMAL",
                "distress_score":   0,
                "condition":        "Stable",
                "possible_cause":   "N/A",
                "prediction":       "Awaiting data...",
                "prediction_confidence": 0.0,
                "confidence_score": round(volume_score, 2),
                "metrics":          {"heart_rate": empty_metric, "spo2": empty_metric, "bp": empty_metric},
                "trend":            "stable",
                "events":           [],
                "recommendations":  [],
                "timeline":         [],
                "alert_explanation": "Insufficient data.",
            }

        # ── 2. Convert to dicts for service functions ──────────────
        curr_dicts = [_to_dict(v) for v in curr_vitals]
        latest_v = curr_vitals[-1]

        # ── 3. Trend analysis ──────────────────────────────────────
        trends       = analyze_trends(curr_dicts)
        overall_trend = trends.get("overall_trend", "stable")

        # ── 4. Distress scoring ────────────────────────────────────
        distress = calculate_distress(
            heart_rate=latest_v.heart_rate,
            spo2=latest_v.spo2,
            respiratory_rate=latest_v.respiratory_rate or 16.0,
            bp_sys=latest_v.blood_pressure_systolic,
            bp_dia=latest_v.blood_pressure_diastolic,
            trend=overall_trend,
        )
        distress_score = distress["distress_score"]
        risk_level     = distress["risk_level"]

        # ── 5. Event detection & Condition Classification ─────────
        curr_desc = list(reversed(curr_vitals))
        events = IntelligenceService.detect_events(curr_desc)
        condition_data = IntelligenceService.detect_condition(curr_vitals[::-1], trends) # Reverse for newest first

        # ── 6. Prediction ──────────────────────────────────────────
        pred_data = AIEngine.generate_prediction(curr_dicts[-1], trends, distress_score)

        # ── 7. Recommendations & timeline ──────────────────────────
        recommendations = IntelligenceService.generate_recommendations(
            events, distress_score=distress_score, overall_trend=overall_trend, condition_data=condition_data
        )
        start_ts  = current_window_start.isoformat()
        end_ts    = now.isoformat()
        timeline  = IntelligenceService.generate_timeline(events, start_ts, end_ts)

        # ── 8. Confidence Score calculation (Upgrade) ──────────────
        # High data + stable trend → 0.8–1.0
        # Medium → 0.5–0.8
        # Low data → <0.5
        trend_consistency = 1.0 if overall_trend == "stable" else 0.8
        event_frequency = max(0, 1.0 - (len(events) * 0.1))
        
        final_confidence = (volume_score * 0.4) + (trend_consistency * 0.3) + (event_frequency * 0.3)
        final_confidence = round(min(1.0, final_confidence), 2)

        # ── 9. Summarization (metric-aware) ────────────────────────────
        summary_data = generate_summary(curr_dicts, curr_dicts[-1], metric=metric)

        # ── 10. Aggregates for metrics ─────────────────────────────
        c_hr  = [v.heart_rate              for v in curr_vitals]
        c_spo = [v.spo2                    for v in curr_vitals]
        c_bps = [v.blood_pressure_systolic for v in curr_vitals]

        p_hr  = [v.heart_rate              for v in prev_vitals]
        p_spo = [v.spo2                    for v in prev_vitals]
        p_bps = [v.blood_pressure_systolic for v in prev_vitals]

        hr_metric = {
            "avg": _avg(c_hr), "min": _min(c_hr), "max": _max(c_hr),
            "abnormal_frequency": sum(1 for x in c_hr if x > 100 or x < 60),
            "trend":              _get_trend_delta(_avg(c_hr), _avg(p_hr), 5),
            "spikes_drops":       sum(1 for x in c_hr if x > 100),
        }
        spo2_metric = {
            "avg": _avg(c_spo), "min": _min(c_spo), "max": _max(c_spo),
            "abnormal_frequency": sum(1 for x in c_spo if x < 94),
            "trend":              _get_trend_delta(_avg(c_spo), _avg(p_spo), 1.5),
            "spikes_drops":       sum(1 for x in c_spo if x < 94),
        }
        bp_metric = {
            "avg": _avg(c_bps), "min": _min(c_bps), "max": _max(c_bps),
            "abnormal_frequency": sum(1 for x in c_bps if x > 140 or x < 90),
            "trend":              _get_trend_delta(_avg(c_bps), _avg(p_bps), 10),
            "spikes_drops":       sum(1 for x in c_bps if x > 140),
        }

        # ── ML enrichment (Phase 3) — must run before metric override ──────────
        ml_data = AIEngine.get_ml_enrichment(
            heart_rate=latest_v.heart_rate,
            spo2=latest_v.spo2,
            respiratory_rate=latest_v.respiratory_rate or 16.0,
            bp_sys=latest_v.blood_pressure_systolic,
            bp_dia=latest_v.blood_pressure_diastolic,
            rule_risk=risk_level,
        )

        # ── 11. Metric-aware risk overrides ─────────────────────────
        # For single-metric views we derive risk from only that signal's stats
        # so the dashboard's cross-signal risk does not bleed through.
        if metric == "heart_rate":
            hr_avg = hr_metric["avg"]
            if hr_avg > 130 or hr_avg < 45:
                metric_risk = "CRITICAL"
            elif hr_avg > 100 or hr_avg < 55:
                metric_risk = "WARNING"
            else:
                metric_risk = "NORMAL"
            effective_risk      = metric_risk
            effective_condition = summary_data.get("possible_condition", "Heart Rate Analysis")
            effective_obs       = summary_data["key_observation"]
            effective_pred      = summary_data["prediction"]
            effective_cause     = summary_data["possible_cause"]

        elif metric == "spo2":
            spo2_avg = spo2_metric["avg"]
            if spo2_avg < 90:
                metric_risk = "CRITICAL"
            elif spo2_avg < 94:
                metric_risk = "WARNING"
            else:
                metric_risk = "NORMAL"
            effective_risk      = metric_risk
            effective_condition = summary_data.get("possible_condition", "Oxygenation Analysis")
            effective_obs       = summary_data["key_observation"]
            effective_pred      = summary_data["prediction"]
            effective_cause     = summary_data["possible_cause"]

        elif metric == "bp":
            bp_avg = bp_metric["avg"]
            if bp_avg > 180 or bp_avg < 80:
                metric_risk = "CRITICAL"
            elif bp_avg > 140 or bp_avg < 90:
                metric_risk = "WARNING"
            else:
                metric_risk = "NORMAL"
            effective_risk      = metric_risk
            effective_condition = summary_data.get("possible_condition", "Blood Pressure Analysis")
            effective_obs       = summary_data["key_observation"]
            effective_pred      = summary_data["prediction"]
            effective_cause     = summary_data["possible_cause"]

        else:
            # Dashboard — full multi-signal hybrid risk
            effective_risk      = ml_data["hybrid_risk"]
            effective_condition = condition_data["condition"]
            effective_obs       = summary_data["key_observation"]
            effective_pred      = pred_data["prediction"]
            effective_cause     = summary_data["possible_cause"]

        # -- Time-series forecast (Phase 4) ------------------------------------
        history_dicts = [
            {
                "heart_rate":              v.heart_rate,
                "spo2":                    v.spo2,
                "blood_pressure_systolic": v.blood_pressure_systolic,
                "blood_pressure_diastolic": v.blood_pressure_diastolic,
                "respiratory_rate":        getattr(v, "respiratory_rate", None) or 16.0,
            }
            for v in curr_vitals
        ]
        forecast_data = AIEngine.get_forecast_enrichment(history_dicts)

        # -- Anomaly engine enrichment (Phase 5) --------------------------------
        anomaly_data = AIEngine.get_anomaly_enrichment(history_dicts)

        # -- Build base analysis dict (before LLM) ─────────────────────────────
        analysis_result = {
            "window_minutes":      window_minutes,
            "key_observation":     effective_obs,
            "risk_level":          effective_risk,
            "distress_score":      distress_score,
            "condition":           effective_condition,
            "possible_cause":      effective_cause,
            "prediction":          effective_pred,
            "prediction_confidence": pred_data["prediction_confidence"],
            "confidence_score":    final_confidence,
            "metrics": {
                "heart_rate": hr_metric,
                "spo2":       spo2_metric,
                "bp":         bp_metric,
            },
            "trend":               overall_trend,
            "events":              events[:10],
            "recommendations":     recommendations,
            "timeline":            timeline,
            "alert_explanation":   IntelligenceService.explain_alert(
                effective_risk, events, overall_trend, distress_score
            ),
            # -- Phase 3 ML fields --
            "ml_prediction":       ml_data["ml_prediction"],
            "ml_confidence":       ml_data["ml_confidence"],
            "explainability":      ml_data["explainability"],
            # -- Phase 4 forecast fields --
            "vitals_forecast":     forecast_data.get("vitals_forecast"),
            "forecast_risk":       forecast_data.get("forecast_risk", ""),
            "forecast_confidence": forecast_data.get("forecast_confidence", 0.0),
            "forecast_explanation": forecast_data.get("forecast_explanation", ""),
            # -- Phase 5 anomaly/pattern/baseline fields --
            "anomalies":           anomaly_data.get("anomalies", []),
            "patterns":            anomaly_data.get("patterns", {"patterns": [], "has_patterns": False}),
            "baseline":            anomaly_data.get("baseline", {}),
        }

        # -- Phase 6: LLM clinical reasoning (enhancement layer) ────────────────
        # Pass metric so the LLM knows to focus on the right signal
        llm_payload = dict(analysis_result)
        if metric:
            llm_payload["analysis_scope"] = metric  # hint for LLM prompt
        llm_summary = AIEngine.get_llm_enrichment(llm_payload)
        analysis_result["llm_summary"] = llm_summary

        return analysis_result



# ── Observation builder (internal, no duplication) ─────────────────────────────

def _build_observation(
    metric,
    hr_metric, spo2_metric, bp_metric,
    overall_trend, distress, events, total_spikes,
) -> tuple[str, str, str]:
    """
    Returns (key_observation, possible_cause, prediction) strings.
    Centralised so no duplication between per-metric and global branches.
    """
    score      = distress["distress_score"]
    risk_level = distress["risk_level"]
    corr_flags = distress.get("correlation_flags", [])
    reasons    = distress.get("reasons", [])

    # ── Cross-signal correlations (highest priority narrative) ─────
    shock_event = next((e for e in events if e["type"] == "SHOCK_PATTERN"), None)
    if shock_event:
        return (
            f"Shock pattern: BP {bp_metric['avg']} mmHg + HR {hr_metric['avg']} bpm. "
            f"Distress score {score}/100.",
            "Hypovolemic, septic, or cardiogenic shock. Urgent haemodynamic assessment required.",
            "High risk of cardiovascular collapse without immediate intervention.",
        )

    hr_high_and_spo2_low = (
        (hr_metric["trend"] == "increasing" or hr_metric["avg"] > 100)
        and (spo2_metric["trend"] == "decreasing" or spo2_metric["avg"] < 92)
    )
    bp_down_hr_up = (
        bp_metric["trend"] == "decreasing" and hr_metric["trend"] == "increasing"
    )

    if metric == "heart_rate":
        if hr_metric["spikes_drops"] > 5 or (hr_metric["trend"] == "increasing" and hr_metric["avg"] > 100):
            return (
                f"HR averaged {hr_metric['avg']} bpm (max {hr_metric['max']}) with "
                f"{hr_metric['spikes_drops']} spikes — {hr_metric['trend']} trend.",
                "Tachycardia may indicate pain, agitation, fever, or hypovolemia.",
                "If rising trend continues, tachycardia may worsen over the next 30 minutes.",
            )
        if hr_metric["trend"] == "decreasing" and hr_metric["avg"] < 60:
            return (
                f"HR averaged {hr_metric['avg']} bpm (min {hr_metric['min']}) — trending into bradycardia.",
                "Medication effect, vagal response, or developing heart block.",
                "Patient may become symptomatic if heart rate drops further.",
            )
        return (
            f"HR averaged {hr_metric['avg']} bpm (min {hr_metric['min']}, max {hr_metric['max']}). "
            f"Trend: {hr_metric['trend']}.",
            "Normal physiological state with stable cardiac rhythm.",
            "Patient expected to remain stable over the next 30 minutes.",
        )

    if metric == "spo2":
        if spo2_metric["spikes_drops"] > 5 or spo2_metric["trend"] == "decreasing":
            sev = "CRITICAL" if spo2_metric["avg"] < 92 else "WARNING"
            return (
                f"SpO₂ averaged {spo2_metric['avg']}% (min {spo2_metric['min']}%) with "
                f"{spo2_metric['spikes_drops']} drops — {spo2_metric['trend']} trend.",
                "Respiratory distress or transient airway obstruction.",
                "Immediate O₂ therapy may be required to prevent severe hypoxia.",
            )
        return (
            f"SpO₂ averaged {spo2_metric['avg']}% (min {spo2_metric['min']}%). "
            f"Trend: {spo2_metric['trend']}.",
            "Adequate oxygenation without signs of respiratory distress.",
            "Patient expected to remain stable over the next 30 minutes.",
        )

    if metric == "bp":
        if bp_metric["trend"] == "increasing" and bp_metric["avg"] > 130:
            return (
                f"BP averaged {bp_metric['avg']} mmHg (max {bp_metric['max']}) — rising trend.",
                "Hypertension episode — possible stress or pain response.",
                "Rising BP trend may indicate potential instability if sustained.",
            )
        if bp_metric["trend"] == "decreasing" and bp_metric["avg"] < 90:
            return (
                f"BP averaged {bp_metric['avg']} mmHg (min {bp_metric['min']}) — falling critically.",
                "Possible haemorrhage, severe dehydration, or vasodilation.",
                "High risk of haemodynamic instability if BP continues to fall.",
            )
        return (
            f"BP averaged {bp_metric['avg']} mmHg (min {bp_metric['min']}, max {bp_metric['max']}). "
            f"Trend: {bp_metric['trend']}.",
            "Stable haemodynamics.",
            "Patient expected to remain stable over the next 30 minutes.",
        )

    # ── Global (no specific metric) ────────────────────────────────
    if hr_high_and_spo2_low:
        return (
            f"Concurrent HR rise (avg {hr_metric['avg']} bpm) and SpO₂ drop (avg {spo2_metric['avg']}%). "
            f"Distress score {score}/100.",
            "High probability of respiratory distress, pulmonary embolism, or shock.",
            "Patient condition is deteriorating. Immediate clinical review required.",
        )

    if bp_down_hr_up:
        return (
            f"Falling BP (avg {bp_metric['avg']} mmHg) with compensatory tachycardia "
            f"(avg {hr_metric['avg']} bpm). Distress {score}/100.",
            "Possible hypovolemic or septic shock.",
            "High risk of cardiovascular collapse if trend continues.",
        )

    if corr_flags:
        return (
            corr_flags[0] + f" Distress score {score}/100.",
            "Multi-metric correlation suggests active physiological stress.",
            "Condition may worsen within 30 minutes without targeted intervention.",
        )

    if total_spikes > 10:
        return (
            f"Multiple abnormal events across HR, SpO₂, and BP ({total_spikes} total). "
            f"Distress score {score}/100.",
            "Patient instability, possible pain, agitation, or evolving illness.",
            "Fluctuating vitals may escalate if the underlying cause is not addressed.",
        )

    # Stable baseline
    return (
        f"HR avg {hr_metric['avg']} bpm, SpO₂ {spo2_metric['avg']}%, "
        f"BP {bp_metric['avg']} mmHg. Trend: {overall_trend}. Distress score {score}/100.",
        "Patient is physiologically stable with no adverse multi-metric correlations.",
        "Stable condition expected to continue over the next 30 minutes.",
    )
