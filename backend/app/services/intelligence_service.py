"""
intelligence_service.py
-----------------------
Stateless clinical intelligence layer.

Responsibilities:
    • detect_events()           – sustained / sudden vital-sign events with deduplication
    • generate_recommendations() – multi-metric correlation recommendations
    • generate_timeline()        – top-N chronological event timeline
    • explain_alert()            – distress-aware, human-readable alert explanation
"""

from datetime import datetime, timezone
from typing import List, Dict, Any, Optional


class IntelligenceService:

    # ──────────────────────────────────────────────────────────────
    # 1. EVENT DETECTION
    # ──────────────────────────────────────────────────────────────
    @staticmethod
    def detect_events(vitals: List[Any]) -> List[Dict]:
        """
        Scan a window of vitals (DB model objects, newest-first) and surface
        clinically meaningful events.

        Each event has:
            type, severity, timestamp, description, priority
        """
        if not vitals:
            return []

        # Work chronologically (oldest → newest) for sequential detection
        chrono = list(reversed(vitals))

        events: List[Dict] = []

        hr_high_streak  = 0
        hr_low_streak   = 0
        spo2_low_streak = 0
        bp_high_streak  = 0
        bp_low_streak   = 0

        hr_spike_groups:   List[Dict] = []
        spo2_drop_groups:  List[Dict] = []
        bp_high_groups:    List[Dict] = []
        bp_low_groups:     List[Dict] = []
        shock_flags:       List[Dict] = []

        for i, v in enumerate(chrono):
            ts  = v.timestamp.isoformat()
            hr  = v.heart_rate
            sp  = v.spo2
            bps = v.blood_pressure_systolic

            # ── Heart-rate high ────────────────────────────────────
            sudden_hr_jump = (i > 0 and (hr - chrono[i - 1].heart_rate) > 15)

            if hr > 100 or sudden_hr_jump:
                hr_high_streak += 1
                hr_low_streak   = 0
            else:
                hr_high_streak  = 0

            if hr_high_streak >= 3 or sudden_hr_jump:
                severity = "CRITICAL" if hr > 120 else "WARNING"
                desc = (
                    f"Sudden heart rate spike to {int(hr)} bpm detected."
                    if sudden_hr_jump
                    else f"Sustained elevated heart rate at {int(hr)} bpm."
                )
                hr_spike_groups.append({
                    "timestamp": ts,
                    "val": hr,
                    "severity": severity,
                    "description": desc,
                    "priority": 85 if severity == "CRITICAL" else 58,
                })
                hr_high_streak = 0  # reset after trigger

            # ── Heart-rate low (bradycardia) ──────────────────────
            if hr < 55:
                hr_low_streak += 1
            else:
                hr_low_streak = 0

            if hr_low_streak >= 3:
                severity = "CRITICAL" if hr < 45 else "WARNING"
                events.append({
                    "type":        "BRADYCARDIA",
                    "severity":    severity,
                    "timestamp":   ts,
                    "description": f"Sustained bradycardia — HR at {int(hr)} bpm.",
                    "priority":    80 if severity == "CRITICAL" else 55,
                })
                hr_low_streak = 0

            # ── SpO2 low ───────────────────────────────────────────
            sudden_spo2_drop = (i > 0 and (chrono[i - 1].spo2 - sp) > 3)

            if sp < 94 or sudden_spo2_drop:
                spo2_low_streak += 1
            else:
                spo2_low_streak = 0

            if spo2_low_streak >= 2 or sudden_spo2_drop:
                severity = "CRITICAL" if sp < 90 else "WARNING"
                desc = (
                    f"Sudden SpO₂ drop to {int(sp)}% detected."
                    if sudden_spo2_drop
                    else f"Sustained low oxygen saturation at {int(sp)}%."
                )
                spo2_drop_groups.append({
                    "timestamp": ts,
                    "val": sp,
                    "severity": severity,
                    "description": desc,
                    "priority": 100 if severity == "CRITICAL" else 80,
                })
                spo2_low_streak = 0

            # ── BP high ────────────────────────────────────────────
            if bps > 140:
                bp_high_streak += 1
                bp_low_streak   = 0
            else:
                bp_high_streak  = 0

            if bp_high_streak >= 3:
                severity = "CRITICAL" if bps > 160 else "WARNING"
                bp_high_groups.append({
                    "timestamp": ts,
                    "val": bps,
                    "severity": severity,
                    "description": f"Elevated systolic BP at {int(bps)} mmHg.",
                    "priority": 72 if severity == "CRITICAL" else 42,
                })
                bp_high_streak = 0

            # ── BP low (hypotension) ───────────────────────────────
            if bps < 90:
                bp_low_streak += 1
            else:
                bp_low_streak = 0

            if bp_low_streak >= 2:
                severity = "CRITICAL" if bps < 80 else "WARNING"
                bp_low_groups.append({
                    "timestamp": ts,
                    "val": bps,
                    "severity": severity,
                    "description": f"Hypotension — systolic BP at {int(bps)} mmHg.",
                    "priority": 90 if severity == "CRITICAL" else 65,
                })
                bp_low_streak = 0

            # ── Shock pattern correlation ──────────────────────────
            if bps < 90 and hr > 100:
                shock_flags.append({
                    "timestamp": ts,
                    "bps": bps,
                    "hr": hr,
                })

        # ── Consolidate HR spikes ──────────────────────────────────
        if hr_spike_groups:
            if len(hr_spike_groups) > 2:
                latest = hr_spike_groups[-1]
                events.append({
                    "type":        "HR_SPIKE",
                    "severity":    latest["severity"],
                    "timestamp":   latest["timestamp"],
                    "description": (
                        f"Repeated HR spikes detected ({len(hr_spike_groups)} episodes). "
                        f"Latest peak at {int(latest['val'])} bpm."
                    ),
                    "priority": 88 if latest["severity"] == "CRITICAL" else 62,
                })
            else:
                for g in hr_spike_groups:
                    events.append({
                        "type":        "HR_SPIKE",
                        "severity":    g["severity"],
                        "timestamp":   g["timestamp"],
                        "description": g["description"],
                        "priority":    g["priority"],
                    })

        # ── Consolidate SpO2 drops ─────────────────────────────────
        if spo2_drop_groups:
            worst_sev = "CRITICAL" if any(g["severity"] == "CRITICAL" for g in spo2_drop_groups) else "WARNING"
            if len(spo2_drop_groups) > 2:
                latest = spo2_drop_groups[-1]
                events.append({
                    "type":        "SPO2_DROP",
                    "severity":    worst_sev,
                    "timestamp":   latest["timestamp"],
                    "description": (
                        f"Multiple O₂ desaturations ({len(spo2_drop_groups)} events). "
                        f"Lowest SpO₂: {int(min(g['val'] for g in spo2_drop_groups))}%."
                    ),
                    "priority": 100,
                })
            else:
                for g in spo2_drop_groups:
                    events.append({
                        "type":        "SPO2_DROP",
                        "severity":    g["severity"],
                        "timestamp":   g["timestamp"],
                        "description": g["description"],
                        "priority":    g["priority"],
                    })

        # ── Consolidate BP high ────────────────────────────────────
        if bp_high_groups:
            if len(bp_high_groups) > 2:
                latest = bp_high_groups[-1]
                events.append({
                    "type":        "BP_HYPERTENSION",
                    "severity":    latest["severity"],
                    "timestamp":   latest["timestamp"],
                    "description": (
                        f"Sustained hypertension ({len(bp_high_groups)} episodes). "
                        f"Peak systolic: {int(max(g['val'] for g in bp_high_groups))} mmHg."
                    ),
                    "priority": 72 if latest["severity"] == "CRITICAL" else 45,
                })
            else:
                for g in bp_high_groups:
                    events.append({
                        "type":        "BP_HYPERTENSION",
                        "severity":    g["severity"],
                        "timestamp":   g["timestamp"],
                        "description": g["description"],
                        "priority":    g["priority"],
                    })

        # ── Consolidate BP low ─────────────────────────────────────
        for g in bp_low_groups:
            events.append({
                "type":        "BP_HYPOTENSION",
                "severity":    g["severity"],
                "timestamp":   g["timestamp"],
                "description": g["description"],
                "priority":    g["priority"],
            })

        # ── Shock correlation event ────────────────────────────────
        if len(shock_flags) >= 2:
            latest = shock_flags[-1]
            events.append({
                "type":        "SHOCK_PATTERN",
                "severity":    "CRITICAL",
                "timestamp":   latest["timestamp"],
                "description": (
                    f"Shock pattern detected — hypotension (BP {int(latest['bps'])} mmHg) "
                    f"with compensatory tachycardia (HR {int(latest['hr'])} bpm) "
                    f"across {len(shock_flags)} readings."
                ),
                "priority": 98,
            })

        # Sort by priority desc, then newest timestamp first
        events.sort(key=lambda x: (x["priority"], x["timestamp"]), reverse=True)
        return events

    # ──────────────────────────────────────────────────────────────
    # 2. CONDITION CLASSIFICATION
    # ──────────────────────────────────────────────────────────────
    @staticmethod
    def detect_condition(vitals: List[Any], trends: Dict) -> Dict:
        """
        Identify clinical conditions from multi-metric patterns and trends.
        """
        if not vitals:
            return {"condition": "Stable", "severity": "LOW"}

        latest = vitals[0]
        hr = latest.heart_rate
        spo2 = latest.spo2
        bps = latest.blood_pressure_systolic

        hr_trend = trends.get("heart_rate", {}).get("direction", "stable")
        spo2_trend = trends.get("spo2", {}).get("direction", "stable")
        # BP trend usually comes from a "bp" or "blood_pressure" key
        bp_trend = trends.get("bp", {}).get("direction", "stable")

        # HR ↑ + SpO2 ↓ → "Respiratory Distress"
        if hr_trend == "rising" and spo2_trend == "falling" and spo2 < 94:
            return {"condition": "Respiratory Distress", "severity": "HIGH"}
        
        # BP ↓ + HR ↑ → "Shock Risk"
        if bp_trend == "falling" and hr_trend == "rising" and bps < 90:
            return {"condition": "Shock Risk", "severity": "HIGH"}
        
        # SpO2 consistently low → "Hypoxia"
        if spo2 < 92:
            return {"condition": "Hypoxia", "severity": "HIGH"}
        
        # HR high only → "Cardiac Stress"
        if hr > 110:
            return {"condition": "Cardiac Stress", "severity": "MODERATE"}

        if spo2 < 95 or hr > 100 or bps > 140 or bps < 95:
             return {"condition": "Observation Required", "severity": "LOW"}

        return {"condition": "Stable", "severity": "LOW"}

    # ──────────────────────────────────────────────────────────────
    # 3. RECOMMENDATIONS
    # ──────────────────────────────────────────────────────────────
    @staticmethod
    def generate_recommendations(
        events: List[Dict],
        distress_score: int = 0,
        overall_trend: str = "stable",
        condition_data: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Generate prioritised clinical action recommendations based on:
            - Detected events
            - Distress score
            - Multi-metric correlations
            - Detected clinical condition (Phase 2)
        """
        recommendations: List[Dict] = []
        condition = condition_data.get("condition") if condition_data else None

        # Helper to add recommendation with all required fields
        def add_rec(cond: str, action: str, text: str, priority_str: str, priority_val: int):
            recommendations.append({
                "condition": cond,
                "action": action,
                "text": text,
                "priority": priority_str,
                "priority_int": priority_val
            })

        # 1. Condition-based recommendations (Phase 2)
        if condition == "Respiratory Distress":
            add_rec("Respiratory Distress", "Administer oxygen support", "Administer oxygen support and check airway obstruction immediately.", "HIGH", 100)
        elif condition == "Shock Risk":
            add_rec("Shock Risk", "Monitor blood pressure closely", "Monitor blood pressure closely and prepare IV fluids. Clinical review required.", "HIGH", 100)
        elif condition == "Hypoxia":
            add_rec("Hypoxia", "Increase O2 titration", "Increase O2 titration and monitor SpO2 trend. Check for airway obstruction.", "HIGH", 95)
        elif condition == "Cardiac Stress":
            add_rec("Cardiac Stress", "Evaluate for stress/pain", "Evaluate for physiological stress, pain, or fever. Consider ECG.", "MEDIUM", 70)

        # 2. Event-based recommendations
        has_shock = any(e["type"] == "SHOCK_PATTERN" for e in events)
        if has_shock and condition != "Shock Risk":
            add_rec("Shock Pattern", "Immediate clinical escalation", "Immediate clinical escalation. Prepare for fluid challenge/vasopressors.", "HIGH", 100)

        has_spo2_drop = any(e["type"] == "SPO2_DROP" for e in events)
        if has_spo2_drop and condition not in ["Respiratory Distress", "Hypoxia"]:
             add_rec("Oxygen Desaturation", "Titrate supplemental O2", "Monitor O2 levels and check airway. Consider titration.", "MEDIUM", 85)

        has_brady = any(e["type"] == "BRADYCARDIA" for e in events)
        if has_brady:
            add_rec("Bradycardia", "Assess haemodynamic impact", "Assess haemodynamic impact. Review medications (beta-blockers). Prepare atropine.", "HIGH", 80)

        # 3. Trend/Distress based
        if overall_trend == "worsening" and distress_score >= 35:
            add_rec("Deteriorating Trend", "Increase monitoring", "Patient condition is worsening. Increase monitoring frequency and notify nurse.", "MEDIUM", 65)

        # 4. Default stable
        if not recommendations:
            add_rec("Stable", "Routine monitoring", "Continue routine monitoring per ICU protocol.", "LOW", 0)

        # Sort by priority_int desc
        recommendations.sort(key=lambda x: x["priority_int"], reverse=True)
        
        # Clean up internal fields for schema compliance
        for r in recommendations:
            r.pop("priority_int", None)

        return recommendations

    # ──────────────────────────────────────────────────────────────
    # 3. TIMELINE
    # ──────────────────────────────────────────────────────────────
    @staticmethod
    def generate_timeline(
        events: List[Dict],
        start_timestamp: str,
        end_timestamp: str,
        max_events: int = 7,
    ) -> List[Dict]:
        """
        Return a concise chronological timeline (top max_events by priority).
        """
        timeline: List[Dict] = [{"timestamp": start_timestamp, "event": "Monitoring window started"}]

        # Keep highest-priority events then sort chronologically
        top_events = sorted(events, key=lambda x: x["priority"], reverse=True)[:max_events]
        chrono = sorted(top_events, key=lambda x: x["timestamp"])

        for e in chrono:
            timeline.append({"timestamp": e["timestamp"], "event": e["description"]})

        if not chrono:
            timeline.append({
                "timestamp": end_timestamp,
                "event": "Patient remained stable — no significant events detected",
            })

        return timeline

    # ──────────────────────────────────────────────────────────────
    # 4. ALERT EXPLANATION
    # ──────────────────────────────────────────────────────────────
    @staticmethod
    def explain_alert(
        alert_level: str,
        events: List[Dict],
        trend: str,
        distress_score: int = 0,
    ) -> str:
        """
        Produce a concise human-readable explanation anchored in:
            distress_score + top_event + overall_trend
        """
        if alert_level in ("INFO", "NORMAL") and distress_score < 35:
            return (
                f"Patient vitals are within acceptable limits. "
                f"Distress score: {distress_score}/100. Trend: {trend}."
            )

        if not events:
            return (
                f"Patient is exhibiting a {trend} trend with a distress score of "
                f"{distress_score}/100, though no acute event has been individually triggered. "
                "Continuous observation recommended."
            )

        top = events[0]

        if top["severity"] == "CRITICAL" or distress_score >= 70:
            return (
                f"🔴 CRITICAL — Distress score {distress_score}/100. "
                f"{top['description']} "
                f"Overall patient trend is {trend}. Immediate escalation warranted."
            )

        return (
            f"🟡 WARNING — Distress score {distress_score}/100. "
            f"{top['description']} "
            f"Trend is {trend}. Increased monitoring advised."
        )
