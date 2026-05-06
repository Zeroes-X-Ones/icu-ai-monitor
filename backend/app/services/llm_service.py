"""
llm_service.py
--------------
LLM-powered clinical reasoning engine (enhancement layer only).

This module uses an LLM (Google Gemini or OpenAI) to convert structured AI
analysis output into human-readable clinical reasoning.  It is purely an
*explanation* layer — it NEVER overrides, replaces, or modifies any
deterministic system logic (distress scoring, ML prediction, anomaly
detection, etc.).

Architecture
    structured_data → prompt assembly → LLM call → parsed response
                                           ↓ (on failure)
                                    rule-based fallback

Supported backends (auto-detected via env vars):
    1. GEMINI_API_KEY  → Google Generative AI  (preferred)
    2. OPENAI_API_KEY  → OpenAI GPT-4o-mini

If neither key is set, or the API call fails, the service falls back to
a deterministic rule-based summary generator (medical_summarizer style)
so the pipeline is never interrupted.

Temperature is kept at 0.2 for clinical safety (low hallucination risk).
"""

from __future__ import annotations

import json
import logging
import os
import time
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# ── LLM Backend Detection ────────────────────────────────────────────────────

_GEMINI_KEY: Optional[str] = os.environ.get("GEMINI_API_KEY")
_OPENAI_KEY: Optional[str] = os.environ.get("OPENAI_API_KEY")

_LLM_BACKEND: Optional[str] = None
_gemini_model = None
_openai_client = None

# Lazy-initialise on first call so import never blocks startup
_initialised = False


def _lazy_init():
    """
    Initialise the LLM backend on first use.
    We do this lazily so that:
        - import time is zero (no network calls during startup)
        - missing SDK → graceful fallback, not crash
    """
    global _initialised, _LLM_BACKEND, _gemini_model, _openai_client, _GEMINI_KEY, _OPENAI_KEY

    if _initialised:
        return
    _initialised = True

    # Re-read env in case .env was loaded after module import
    _GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
    _OPENAI_KEY = os.environ.get("OPENAI_API_KEY")

    # --- Try Gemini first ---
    if _GEMINI_KEY:
        try:
            import google.generativeai as genai
            genai.configure(api_key=_GEMINI_KEY)
            _gemini_model = genai.GenerativeModel("gemini-2.0-flash")
            _LLM_BACKEND = "gemini"
            logger.info("[llm_service] Gemini backend initialised.")
            return
        except Exception as exc:
            logger.warning("[llm_service] Gemini init failed: %s", exc)

    # --- Fallback: OpenAI ---
    if _OPENAI_KEY:
        try:
            from openai import OpenAI
            _openai_client = OpenAI(api_key=_OPENAI_KEY)
            _LLM_BACKEND = "openai"
            logger.info("[llm_service] OpenAI backend initialised.")
            return
        except Exception as exc:
            logger.warning("[llm_service] OpenAI init failed: %s", exc)

    logger.warning(
        "[llm_service] No LLM API key found (GEMINI_API_KEY / OPENAI_API_KEY). "
        "Running in fallback mode — rule-based summaries only."
    )


# ── Prompt Construction ──────────────────────────────────────────────────────

_SYSTEM_PROMPT = """You are a senior ICU clinical decision-support assistant integrated into a real-time patient monitoring system.

Your role is to INTERPRET structured vitals analysis data and provide clear, clinically relevant reasoning. You must:

RULES:
• Base your reasoning ONLY on the data provided — no assumptions, no hallucinated lab values or diagnoses.
• Be concise and actionable — ICU staff read this under time pressure.
• Use standard medical terminology but remain understandable.
• Never contradict the system's risk_level or distress_score — your job is to EXPLAIN them, not override.
• Do not invent patient history, medications, or demographics not present in the data.
• If data is insufficient, say so explicitly rather than speculating.

OUTPUT FORMAT (respond ONLY with this JSON, no markdown fences):
{
  "clinical_summary": "2-3 sentence clinical interpretation of the patient's current state",
  "risk_explanation": "Why the current risk level is what it is, referencing specific vital signs",
  "recommended_action": "Concrete clinical action(s) to consider, appropriate for the risk level",
  "urgency": "ROUTINE | ELEVATED | URGENT | EMERGENT"
}"""


def _build_user_prompt(data: Dict) -> str:
    """Assemble the user-facing prompt from structured analysis data."""

    # Format events concisely
    events_str = "None detected"
    events = data.get("events", [])
    if events:
        event_lines = []
        for e in events[:5]:  # Cap at 5 for token efficiency
            if isinstance(e, dict):
                event_lines.append(
                    f"  - {e.get('type', 'EVENT')}: {e.get('description', e.get('reason', 'N/A'))}"
                )
            else:
                event_lines.append(f"  - {e}")
        events_str = "\n".join(event_lines)

    # Format anomalies
    anomalies_str = "None"
    anomalies = data.get("anomalies", [])
    if anomalies:
        anom_lines = []
        for a in anomalies[:4]:
            if isinstance(a, dict):
                anom_lines.append(
                    f"  - {a.get('label', a.get('signal', '?'))}: "
                    f"z-score={a.get('z_score', '?')}, severity={a.get('severity', '?')}"
                )
        anomalies_str = "\n".join(anom_lines) if anom_lines else "None"

    # Format patterns
    patterns_str = "None"
    patterns = data.get("patterns", {})
    if isinstance(patterns, dict) and patterns.get("has_patterns"):
        pat_lines = []
        for p in patterns.get("patterns", [])[:3]:
            pat_lines.append(
                f"  - {p.get('pattern', '?')} (confidence: {p.get('confidence', '?')}, "
                f"periodic: {p.get('periodic', False)})"
            )
        patterns_str = "\n".join(pat_lines) if pat_lines else "None"

    # Format baseline
    baseline = data.get("baseline", {})
    baseline_str = "Insufficient data"
    if baseline and baseline.get("sufficient_data"):
        baseline_str = (
            f"HR mean={baseline.get('hr_mean', '?')} bpm, "
            f"SpO2 mean={baseline.get('spo2_mean', '?')}%, "
            f"RR mean={baseline.get('rr_mean', '?')} br/min, "
            f"BP mean={baseline.get('bp_mean', '?')} mmHg "
            f"(from {baseline.get('readings_count', '?')} readings)"
        )

    prompt = f"""Analyse the following ICU patient vitals data and provide your clinical interpretation.

CURRENT VITALS ANALYSIS:
• Distress Score: {data.get('distress_score', 'N/A')}/100
• Risk Level: {data.get('risk_level', 'N/A')}
• Overall Trend: {data.get('trend', 'N/A')}
• Condition: {data.get('condition', 'N/A')}

DETECTED EVENTS:
{events_str}

PREDICTION:
• {data.get('prediction', 'N/A')}
• Confidence: {data.get('prediction_confidence', 'N/A')}

STATISTICAL ANOMALIES (relative to patient baseline):
{anomalies_str}

RECURRENT PATTERNS:
{patterns_str}

PATIENT BASELINE:
{baseline_str}

Provide your clinical interpretation as the specified JSON object."""

    return prompt


# ── LLM Call ─────────────────────────────────────────────────────────────────

_LLM_TEMPERATURE = 0.2
_LLM_MAX_TOKENS  = 400  # Keeps responses concise and cost-effective


def _call_gemini(prompt: str) -> Optional[str]:
    """Call Google Gemini and return the raw text response."""
    try:
        response = _gemini_model.generate_content(
            [
                {"role": "user", "parts": [{"text": _SYSTEM_PROMPT + "\n\n" + prompt}]},
            ],
            generation_config={
                "temperature": _LLM_TEMPERATURE,
                "max_output_tokens": _LLM_MAX_TOKENS,
            },
        )
        return response.text
    except Exception as exc:
        logger.error("[llm_service] Gemini API call failed: %s", exc)
        return None


def _call_openai(prompt: str) -> Optional[str]:
    """Call OpenAI and return the raw text response."""
    try:
        response = _openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=_LLM_TEMPERATURE,
            max_tokens=_LLM_MAX_TOKENS,
        )
        return response.choices[0].message.content
    except Exception as exc:
        logger.error("[llm_service] OpenAI API call failed: %s", exc)
        return None


def _call_llm(prompt: str) -> Optional[str]:
    """Route to the active LLM backend."""
    if _LLM_BACKEND == "gemini":
        return _call_gemini(prompt)
    elif _LLM_BACKEND == "openai":
        return _call_openai(prompt)
    return None


# ── Response Parsing ─────────────────────────────────────────────────────────

def _parse_llm_response(raw: str) -> Optional[Dict]:
    """
    Parse LLM output into a structured dict.
    Handles common LLM quirks: markdown fences, extra whitespace, etc.
    """
    if not raw:
        return None

    # Strip markdown code fences if present
    text = raw.strip()
    if text.startswith("```"):
        # Remove opening fence (```json or ```)
        first_newline = text.index("\n") if "\n" in text else len(text)
        text = text[first_newline + 1:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()

    try:
        result = json.loads(text)
        # Validate expected keys
        required = {"clinical_summary", "risk_explanation", "recommended_action", "urgency"}
        if not required.issubset(result.keys()):
            logger.warning("[llm_service] LLM response missing keys: %s", required - result.keys())
            return None

        # Sanitise urgency to known values
        valid_urgency = {"ROUTINE", "ELEVATED", "URGENT", "EMERGENT"}
        if result.get("urgency", "").upper() not in valid_urgency:
            result["urgency"] = _infer_urgency_from_risk(None)

        result["urgency"] = result["urgency"].upper()
        return result
    except (json.JSONDecodeError, ValueError) as exc:
        logger.warning("[llm_service] Failed to parse LLM JSON: %s", exc)
        return None


# ── Rule-Based Fallback ──────────────────────────────────────────────────────

_URGENCY_MAP = {
    "CRITICAL": "EMERGENT",
    "WARNING":  "ELEVATED",
    "NORMAL":   "ROUTINE",
}


def _infer_urgency_from_risk(risk_level: Optional[str]) -> str:
    return _URGENCY_MAP.get(risk_level or "", "ROUTINE")


def _generate_fallback(data: Dict) -> Dict:
    """
    Deterministic rule-based fallback when LLM is unavailable.
    Mirrors the same output schema as the LLM response so the consumer
    doesn't need to know the source.
    """
    risk        = data.get("risk_level", "NORMAL")
    score       = data.get("distress_score", 0)
    trend       = data.get("trend", "stable")
    condition   = data.get("condition", "Stable")
    prediction  = data.get("prediction", "Patient expected to remain stable.")
    anomalies   = data.get("anomalies", [])
    patterns    = data.get("patterns", {})

    # --- Clinical summary ---
    if risk == "CRITICAL":
        summary = (
            f"Patient is in significant physiological distress (score {score}/100). "
            f"Condition classified as {condition}. "
            f"Trend is {trend} — immediate clinical attention is warranted."
        )
    elif risk == "WARNING":
        summary = (
            f"Early signs of clinical deterioration detected (distress {score}/100). "
            f"Condition: {condition}. Trend: {trend}. "
            f"Close monitoring and reassessment recommended."
        )
    else:
        summary = (
            f"Patient vitals are within acceptable parameters (distress {score}/100). "
            f"Condition: {condition}. Trend: {trend}. "
            f"Continue routine monitoring."
        )

    # --- Risk explanation ---
    risk_parts = []
    if score >= 70:
        risk_parts.append(f"Distress score of {score}/100 indicates critical physiological stress.")
    elif score >= 35:
        risk_parts.append(f"Distress score of {score}/100 shows emerging clinical concern.")
    else:
        risk_parts.append(f"Distress score of {score}/100 is within normal limits.")

    if anomalies:
        for a in anomalies[:2]:
            if isinstance(a, dict):
                risk_parts.append(
                    f"{a.get('label', 'Signal')} deviates {abs(a.get('z_score', 0)):.1f}σ "
                    f"from patient baseline ({a.get('severity', 'WARNING')})."
                )

    if isinstance(patterns, dict) and patterns.get("has_patterns"):
        for p in patterns.get("patterns", [])[:1]:
            risk_parts.append(f"Recurrent pattern detected: {p.get('pattern', 'unknown')}.")

    if trend == "worsening":
        risk_parts.append("Vital signs are trending in an unfavourable direction.")

    risk_explanation = " ".join(risk_parts)

    # --- Recommended action ---
    if risk == "CRITICAL":
        action = (
            "Immediate bedside assessment required. Consider ABG, continuous ECG monitoring, "
            "and prepare for potential escalation of care. Notify attending physician."
        )
    elif risk == "WARNING":
        action = (
            "Increase monitoring frequency to every 5 minutes. Reassess vital trends "
            "and consider targeted interventions if deterioration continues."
        )
    else:
        action = "Continue routine monitoring schedule. No immediate intervention required."

    return {
        "clinical_summary":   summary,
        "risk_explanation":   risk_explanation,
        "recommended_action": action,
        "urgency":            _infer_urgency_from_risk(risk),
        "llm_backend":        "fallback",
    }


# ── Public API ───────────────────────────────────────────────────────────────

def generate_clinical_summary(data: Dict) -> Dict:
    """
    Generate an LLM-powered clinical reasoning summary.

    Parameters
    ----------
    data : dict
        Structured analysis data containing:
            distress_score, risk_level, trend, events, prediction,
            condition, anomalies, patterns, baseline, etc.

    Returns
    -------
    dict
        {
            "clinical_summary":   str,
            "risk_explanation":   str,
            "recommended_action": str,
            "urgency":            str,   # ROUTINE | ELEVATED | URGENT | EMERGENT
            "llm_backend":        str,   # "gemini" | "openai" | "fallback"
        }

    This function NEVER raises — it always returns a valid dict.
    """
    _lazy_init()

    # If no LLM backend is available, go straight to fallback
    if _LLM_BACKEND is None:
        return _generate_fallback(data)

    # Build prompt and call LLM
    try:
        prompt = _build_user_prompt(data)
        start = time.time()
        raw_response = _call_llm(prompt)
        elapsed = time.time() - start
        logger.info("[llm_service] LLM call took %.2fs (backend=%s)", elapsed, _LLM_BACKEND)

        if raw_response:
            parsed = _parse_llm_response(raw_response)
            if parsed:
                parsed["llm_backend"] = _LLM_BACKEND
                return parsed

        # LLM returned empty or unparseable → fallback
        logger.warning("[llm_service] LLM response unusable — falling back to rules.")
    except Exception as exc:
        logger.error("[llm_service] LLM pipeline error: %s — falling back to rules.", exc)

    return _generate_fallback(data)


def is_llm_available() -> bool:
    """Check whether an LLM backend is configured and initialised."""
    _lazy_init()
    return _LLM_BACKEND is not None
