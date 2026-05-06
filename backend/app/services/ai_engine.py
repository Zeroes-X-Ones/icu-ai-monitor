"""
ai_engine.py
------------
Hybrid clinical intelligence pipeline.

Pipeline (per reading):
    1. Distress scoring   (rule-based, always runs)
    2. Trend analysis     (slope-based, always runs)
    3. Event detection    (pattern matching, always runs)
    4. ML prediction      (RandomForest, optional — fails gracefully)
    5. Hybrid decision    (rule + ML combined → final alert_level)
    6. Explainability     (feature importance text)
    7. Summary string     (backward-compatible ai_summary)

Returns (alert_level: str, ai_summary: str) — backward-compatible.
Extended metadata is available via AIEngine.last_ml_meta (thread-unsafe, for logging only)
or consumed directly from vitals_service.get_analysis().
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

from app.schemas.vitals_schema import VitalsCreate
from app.services.distress_detector  import calculate_distress
from app.services.trend_analysis      import analyze_trends
from app.services.intelligence_service import IntelligenceService
from app.services.medical_summarizer  import generate_summary

# -- Lazy import of anomaly engine (never crashes startup) ---------------------
try:
    from app.services.anomaly_engine import detect_anomalies, detect_patterns, build_baseline
    _ANOMALY_AVAILABLE = True
except ImportError:
    _ANOMALY_AVAILABLE = False
    logger.warning("[ai_engine] anomaly_engine not importable -- anomaly detection disabled.")

    def detect_anomalies(history):  # type: ignore
        return []

    def detect_patterns(history):  # type: ignore
        return {"patterns": [], "has_patterns": False}

    def build_baseline(history):  # type: ignore
        return {"hr_mean": 0, "spo2_mean": 0, "rr_mean": 0, "bp_mean": 0,
                "readings_count": 0, "sufficient_data": False}

logger = logging.getLogger(__name__)

# -- Lazy import of ML layer (never crashes startup) --------------------------
try:
    from app.ml.model_loader import predict_risk, get_feature_importance_text
    _ML_AVAILABLE = True
except ImportError:
    _ML_AVAILABLE = False
    logger.warning("[ai_engine] ML module not importable -- running rule-only mode.")

    def predict_risk(*args, **kwargs):  # type: ignore
        return {"ml_risk": None, "ml_confidence": 0.0, "ml_available": False, "class_probs": {}}

    def get_feature_importance_text(*args, **kwargs) -> str:  # type: ignore
        return ""

# -- Lazy import of prediction engine (never crashes startup) ------------------
try:
    from app.services.prediction_engine import predict_future_vitals
    _FORECAST_AVAILABLE = True
except ImportError:
    _FORECAST_AVAILABLE = False
    logger.warning("[ai_engine] prediction_engine not importable -- forecasting disabled.")

    def predict_future_vitals(history):  # type: ignore
        return {
            "forecast": {"spo2": 97.0, "heart_rate": 75.0, "bp_sys": 120.0, "respiratory_rate": 16.0},
            "risk_prediction": "Forecast unavailable",
            "confidence": 0.0,
            "explanation": "Prediction engine not loaded.",
        }

# -- Lazy import of LLM clinical reasoning (never crashes startup) -------------
try:
    from app.services.llm_service import generate_clinical_summary as _llm_summarise
    _LLM_AVAILABLE = True
except ImportError:
    _LLM_AVAILABLE = False
    logger.warning("[ai_engine] llm_service not importable -- LLM reasoning disabled.")

    def _llm_summarise(data):  # type: ignore
        return {
            "clinical_summary": "",
            "risk_explanation": "",
            "recommended_action": "",
            "urgency": "ROUTINE",
            "llm_backend": "unavailable",
        }


# ── Risk level helpers ────────────────────────────────────────────────────────────

_RISK_ORDER = {"NORMAL": 0, "WARNING": 1, "CRITICAL": 2}

def _higher_risk(a: str, b: str) -> str:
    """Return the risk label with the higher severity."""
    return a if _RISK_ORDER.get(a, 0) >= _RISK_ORDER.get(b, 0) else b

def _to_alert_level(risk: str) -> str:
    return "CRITICAL" if risk == "CRITICAL" else "WARNING" if risk == "WARNING" else "INFO"


# ── Hybrid decision logic ─────────────────────────────────────────────────────────

def _hybrid_decision(rule_risk: str, ml_result: Dict) -> Tuple[str, float, str]:
    """
    Combine rule-based risk with ML prediction.

    Strategy
    --------
    - If ML not available → use rule (fail-safe).
    - If both agree        → high-confidence rule result.
    - If mismatch          → safety-first: prefer the higher severity.
      Exception: if ML confidence is very high (≥0.85) and rule is NORMAL,
      escalate to ML's level (catches emerging risks early).

    Returns
    -------
    (final_risk: str, combined_confidence: float, decision_note: str)
    """
    if not ml_result.get("ml_available"):
        return rule_risk, 1.0, "rule-only (ML unavailable)"

    ml_risk  = ml_result["ml_risk"]
    ml_conf  = ml_result["ml_confidence"]

    if rule_risk == ml_risk:
        combined_conf = min(1.0, ml_conf + 0.1)   # agreement bonus
        return rule_risk, round(combined_conf, 4), "rule+ML agree"

    # Mismatch — safety-first
    if rule_risk == "NORMAL" and ml_conf >= 0.85:
        # ML is very confident about a non-normal prediction → trust it
        final = ml_risk
        note  = f"ML override (conf={ml_conf:.2f}): rule=NORMAL, ML={ml_risk}"
        logger.info("[ai_engine] %s", note)
        return final, ml_conf, note

    # Default: take the more conservative (higher severity) reading
    final = _higher_risk(rule_risk, ml_risk)
    note  = f"mismatch: rule={rule_risk}, ML={ml_risk} → kept {final}"
    return final, round(ml_conf * 0.8, 4), note   # lower conf on mismatch


# ── AIEngine ─────────────────────────────────────────────────────────────────────

class AIEngine:

    # ── Short-term prediction (trend-based) ──────────────────────────────────────
    @staticmethod
    def generate_prediction(latest: Dict, trends: Dict, distress_score: int) -> Dict:
        """
        Generate short-term clinical predictions based on trends and distress.
        Returns {prediction, prediction_confidence}.
        """
        hr  = latest.get("heart_rate", 0)
        spo2 = latest.get("spo2", 0)
        bps = latest.get("blood_pressure_systolic", 0)

        hr_trend   = trends.get("heart_rate", {}).get("direction", "stable")
        spo2_trend = trends.get("spo2",       {}).get("direction", "stable")
        bp_trend   = trends.get("bp",         {}).get("direction", "stable")

        prediction = "Patient likely to remain stable"
        confidence = 0.8

        if spo2_trend == "falling" and spo2 < 94:
            prediction = "Risk of hypoxia in next 15–20 minutes"
            confidence = 0.9 if spo2 < 90 else 0.7
        elif hr_trend == "rising" and hr > 100:
            prediction = "Possible tachycardia worsening"
            confidence = 0.85 if hr > 120 else 0.65
        elif bp_trend == "falling" and hr_trend == "rising":
            prediction = "Possible shock risk"
            confidence = 0.9 if bps < 90 else 0.7

        if distress_score > 70:
            confidence = min(confidence + 0.1, 1.0)
        elif distress_score < 10:
            confidence = 0.95

        return {
            "prediction":            prediction,
            "prediction_confidence": round(confidence, 2),
        }

    # ── Hybrid real-time analysis ─────────────────────────────────────────────────
    @staticmethod
    def analyze_realtime(
        vitals: VitalsCreate,
        history: Optional[List[Dict]] = None,
    ) -> Tuple[str, str]:
        """
        Full hybrid pipeline for every incoming vital-sign reading.

        Returns
        -------
        (alert_level: str, ai_summary: str)  — backward-compatible
        """
        history = history or []

        latest_dict: Dict = {
            "heart_rate":              vitals.heart_rate,
            "spo2":                    vitals.spo2,
            "respiratory_rate":        vitals.respiratory_rate or 16.0,
            "blood_pressure_systolic": vitals.blood_pressure_systolic,
            "blood_pressure_diastolic": vitals.blood_pressure_diastolic,
        }

        # Pad history with current reading for trend stability when cold-start
        if not history:
            history = [latest_dict] * 5

        # ── 1. Rule-based distress ───────────────────────────────────────────────
        distress = calculate_distress(
            heart_rate=vitals.heart_rate,
            spo2=vitals.spo2,
            respiratory_rate=vitals.respiratory_rate or 16.0,
            bp_sys=vitals.blood_pressure_systolic,
            bp_dia=vitals.blood_pressure_diastolic,
        )
        rule_risk  = distress["risk_level"]      # NORMAL | WARNING | CRITICAL
        dist_score = distress["distress_score"]
        reasons    = distress["reasons"]
        corr_flags = distress.get("correlation_flags", [])

        # ── 2. ML prediction ─────────────────────────────────────────────────────
        ml_result = predict_risk(
            heart_rate=vitals.heart_rate,
            spo2=vitals.spo2,
            respiratory_rate=vitals.respiratory_rate or 16.0,
            bp_sys=vitals.blood_pressure_systolic,
            bp_dia=vitals.blood_pressure_diastolic,
        )

        # ── 3. Hybrid decision ───────────────────────────────────────────────────
        final_risk, hybrid_conf, decision_note = _hybrid_decision(rule_risk, ml_result)
        alert_level = _to_alert_level(final_risk)

        # ── 4. Explainability ────────────────────────────────────────────────────
        explainability = get_feature_importance_text(
            vitals.heart_rate,
            vitals.spo2,
            vitals.respiratory_rate or 16.0,
            vitals.blood_pressure_systolic,
            vitals.blood_pressure_diastolic,
        )

        # ── 5. Medical summary ───────────────────────────────────────────────────
        summary_data    = generate_summary(history, latest_dict)

        # ── 6. Trend / condition context ─────────────────────────────────────────
        trends = analyze_trends(history)

        class _DummyVital:
            """Minimal object wrapper so IntelligenceService works on dicts."""
            __slots__ = ("heart_rate", "spo2", "blood_pressure_systolic",
                         "blood_pressure_diastolic", "timestamp")
            def __init__(self, d: Dict):
                self.heart_rate              = d["heart_rate"]
                self.spo2                    = d["spo2"]
                self.blood_pressure_systolic = d["blood_pressure_systolic"]
                self.blood_pressure_diastolic = d["blood_pressure_diastolic"]
                self.timestamp               = datetime.now(timezone.utc)

        vitals_objs   = [_DummyVital(h) for h in reversed(history)]
        condition_data = IntelligenceService.detect_condition(vitals_objs, trends)

        # -- 7a. Time-series forecast -----------------------------------------
        forecast_data = predict_future_vitals(history)

        # -- 7c. Anomaly detection, patterns, baseline -------------------------
        try:
            anomalies = detect_anomalies(history)
            patterns  = detect_patterns(history)
            baseline  = build_baseline(history)
        except Exception as exc:
            logger.error("[ai_engine] Anomaly engine error: %s", exc)
            anomalies = []
            patterns  = {"patterns": [], "has_patterns": False}
            baseline  = {"hr_mean": 0, "spo2_mean": 0, "rr_mean": 0, "bp_mean": 0,
                         "readings_count": 0, "sufficient_data": False}

        # -- 7b. Build ai_summary string (backward-compatible) -----------------
        parts: List[str] = []

        if corr_flags:
            parts.append(corr_flags[0])
        elif reasons:
            parts.append(reasons[0])

        parts += [r for r in reasons if r not in parts][:1]
        parts.append(f"Distress: {dist_score}/100.")

        if ml_result.get("ml_available"):
            ml_conf_pct = int(ml_result["ml_confidence"] * 100)
            parts.append(
                f"ML prediction: {ml_result['ml_risk']} ({ml_conf_pct}% confidence)."
            )

        if explainability:
            parts.append(explainability)

        # Add forecast risk to summary if non-trivial
        fr = forecast_data.get("risk_prediction", "")
        if fr and "stable" not in fr.lower() and "insufficient" not in fr.lower():
            parts.append(f"Forecast: {fr}.")

        # Add anomaly context to summary (limit to first 2 to keep concise)
        for anom in anomalies[:2]:
            parts.append(
                f"Anomaly: {anom['label']} deviation ({anom['severity']}, "
                f"z={anom['z_score']})."
            )

        # Add pattern context to summary
        if patterns.get("has_patterns"):
            for pat in patterns["patterns"][:1]:
                parts.append(f"Pattern: {pat['pattern']} (confidence {pat['confidence']}).")

        if alert_level == "CRITICAL":
            parts.append("Immediate clinical review required.")
        elif alert_level == "WARNING":
            parts.append("Increased monitoring advised.")
        else:
            parts.append("Vitals within acceptable range.")

        ai_summary = " ".join(parts)
        return alert_level, ai_summary

    # ── ML-enhanced analysis (used by vitals_service.get_analysis) ───────────────
    @staticmethod
    def get_ml_enrichment(
        heart_rate: float,
        spo2: float,
        respiratory_rate: float,
        bp_sys: float,
        bp_dia: float,
        rule_risk: str,
    ) -> Dict:
        """
        Run the ML layer and return a dict of ML-specific fields to be merged
        into the AnalysisResponse by vitals_service.get_analysis().

        Returns
        -------
        {
            "ml_prediction"  : str,
            "ml_confidence"  : float,
            "explainability" : str,
            "ml_available"   : bool,
            "hybrid_risk"    : str,   # final combined risk
        }
        """
        ml_result = predict_risk(
            heart_rate=heart_rate,
            spo2=spo2,
            respiratory_rate=respiratory_rate,
            bp_sys=bp_sys,
            bp_dia=bp_dia,
        )

        final_risk, _, _ = _hybrid_decision(rule_risk, ml_result)

        explainability = get_feature_importance_text(
            heart_rate, spo2, respiratory_rate, bp_sys, bp_dia
        )

        return {
            "ml_prediction":  ml_result.get("ml_risk") or rule_risk,
            "ml_confidence":  ml_result.get("ml_confidence", 0.0),
            "explainability": explainability,
            "ml_available":   ml_result.get("ml_available", False),
            "hybrid_risk":    final_risk,
        }

    # -- Time-series forecast (used by vitals_service.get_analysis) ------------
    @staticmethod
    def get_forecast_enrichment(history: List[Dict]) -> Dict:
        """
        Run the prediction engine and return forecast fields to merge
        into AnalysisResponse.

        Returns
        -------
        {
            "vitals_forecast":      dict,  # {spo2, heart_rate, bp_sys, respiratory_rate}
            "forecast_risk":        str,
            "forecast_confidence":  float,
            "forecast_explanation": str,
        }
        """
        try:
            result = predict_future_vitals(history)
            return {
                "vitals_forecast":      result["forecast"],
                "forecast_risk":        result["risk_prediction"],
                "forecast_confidence":  result["confidence"],
                "forecast_explanation": result["explanation"],
            }
        except Exception as exc:
            logger.error("[ai_engine] Forecast failed: %s", exc)
            return {
                "vitals_forecast":      None,
                "forecast_risk":        "",
                "forecast_confidence":  0.0,
                "forecast_explanation": "Forecast unavailable due to internal error.",
            }

    # ── Anomaly enrichment (used by vitals_service.get_analysis) ──────────────
    @staticmethod
    def get_anomaly_enrichment(history: List[Dict]) -> Dict:
        """
        Run anomaly detection, pattern detection, and baseline profiling.

        Returns
        -------
        {
            "anomalies": list,
            "patterns":  dict,
            "baseline":  dict,
        }
        """
        try:
            return {
                "anomalies": detect_anomalies(history),
                "patterns":  detect_patterns(history),
                "baseline":  build_baseline(history),
            }
        except Exception as exc:
            logger.error("[ai_engine] Anomaly enrichment failed: %s", exc)
            return {
                "anomalies": [],
                "patterns":  {"patterns": [], "has_patterns": False},
                "baseline":  {"hr_mean": 0, "spo2_mean": 0, "rr_mean": 0, "bp_mean": 0,
                              "readings_count": 0, "sufficient_data": False},
            }

    # ── LLM clinical reasoning (used by vitals_service.get_analysis) ──────────
    @staticmethod
    def get_llm_enrichment(analysis_data: Dict) -> Dict:
        """
        Generate an LLM-powered clinical reasoning summary.

        The LLM is an *explanation layer only* — it interprets the structured
        analysis data but NEVER overrides risk levels, scores, or decisions.

        Parameters
        ----------
        analysis_data : dict
            The full structured analysis dict (distress_score, risk_level,
            trend, events, prediction, condition, anomalies, patterns, etc.)

        Returns
        -------
        {
            "clinical_summary":   str,
            "risk_explanation":   str,
            "recommended_action": str,
            "urgency":            str,
            "llm_backend":        str,
        }
        """
        try:
            return _llm_summarise(analysis_data)
        except Exception as exc:
            logger.error("[ai_engine] LLM enrichment failed: %s", exc)
            return {
                "clinical_summary":   "",
                "risk_explanation":   "",
                "recommended_action": "",
                "urgency":            "ROUTINE",
                "llm_backend":        "error",
            }
