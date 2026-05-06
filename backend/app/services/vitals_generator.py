
# import random
# import time
# from collections import deque
# from datetime import datetime

# # Store last 60 readings (1 per second × 60 seconds)
# MAX_HISTORY = 60

# vitals_history = deque(maxlen=MAX_HISTORY)

# # Simulated patient state — drifts over time for realism
# _patient_state = {
#     "hr_base": 78,
#     "spo2_base": 97,
#     "rr_base": 16,
#     "bp_sys_base": 120,
#     "bp_dia_base": 80,
#     "drift_direction": 1,
#     "drift_steps": 0,
# }


# def _drift_base_values():
#     """Slowly drift base vitals to simulate patient condition changes."""
#     state = _patient_state
#     state["drift_steps"] += 1

#     if state["drift_steps"] > 20:
#         state["drift_direction"] *= -1
#         state["drift_steps"] = 0

#     state["hr_base"] = max(60, min(115, state["hr_base"] + state["drift_direction"] * random.uniform(0, 0.5)))
#     state["spo2_base"] = max(88, min(100, state["spo2_base"] - state["drift_direction"] * random.uniform(0, 0.15)))
#     state["rr_base"] = max(12, min(27, state["rr_base"] + state["drift_direction"] * random.uniform(0, 0.2)))
    
#     # Drift BP
#     state["bp_sys_base"] = max(90, min(180, state["bp_sys_base"] + state["drift_direction"] * random.uniform(0, 0.5)))
#     state["bp_dia_base"] = max(60, min(110, state["bp_dia_base"] + state["drift_direction"] * random.uniform(0, 0.3)))


# def generate_vitals() -> dict:
#     """Generate a single vitals reading with realistic noise."""
#     _drift_base_values()

#     # Keep float precision for internal realism
#     heart_rate = _patient_state["hr_base"] + random.uniform(-3, 3)
#     spo2 = _patient_state["spo2_base"] + random.uniform(-0.5, 0.5)
#     respiratory_rate = _patient_state["rr_base"] + random.uniform(-1, 1)

#     bp_sys = _patient_state["bp_sys_base"] + random.uniform(-2, 2)
#     bp_dia = _patient_state["bp_dia_base"] + random.uniform(-2, 2)

#     # Clamp
#     heart_rate = max(60, min(120, heart_rate))
#     spo2 = max(88, min(100, spo2))
#     respiratory_rate = max(12, min(28, respiratory_rate))
#     bp_sys = max(80, min(200, bp_sys))
#     bp_dia = max(50, min(130, bp_dia))

#     # ✅ FINAL FIX: convert to correct types for backend
#     reading = {
#         "timestamp": datetime.utcnow().isoformat(),
#         "heart_rate": int(round(heart_rate)),
#         "spo2": int(round(spo2)),
#         "respiratory_rate": int(round(respiratory_rate)),
#         "blood_pressure_systolic": int(round(bp_sys)),
#         "blood_pressure_diastolic": int(round(bp_dia))
#     }

#     vitals_history.append(reading)
#     return reading


# def get_history() -> list:
#     """Return all stored vitals history."""
#     return list(vitals_history)


# def get_latest() -> dict | None:
#     """Return the most recent vitals reading."""
#     if vitals_history:
#         return vitals_history[-1]
#     return None


import random
from collections import deque
from datetime import datetime, timezone

# Keep small local cache (optional, not primary source)
MAX_HISTORY = 60
vitals_history = deque(maxlen=MAX_HISTORY)

# Simulated patient state
_patient_state = {
    "hr_base": 78,
    "spo2_base": 97,
    "rr_base": 16,
    "bp_sys_base": 120,
    "bp_dia_base": 80,
    "drift_direction": 1,
    "drift_steps": 0,
}


def _drift_base_values():
    state = _patient_state
    state["drift_steps"] += 1

    if state["drift_steps"] > 20:
        state["drift_direction"] *= -1
        state["drift_steps"] = 0

    state["hr_base"] = max(60, min(115, state["hr_base"] + state["drift_direction"] * random.uniform(0, 0.5)))
    state["spo2_base"] = max(88, min(100, state["spo2_base"] - state["drift_direction"] * random.uniform(0, 0.15)))
    state["rr_base"] = max(12, min(27, state["rr_base"] + state["drift_direction"] * random.uniform(0, 0.2)))

    state["bp_sys_base"] = max(90, min(180, state["bp_sys_base"] + state["drift_direction"] * random.uniform(0, 0.5)))
    state["bp_dia_base"] = max(60, min(110, state["bp_dia_base"] + state["drift_direction"] * random.uniform(0, 0.3)))


def generate_vitals() -> dict:
    _drift_base_values()

    heart_rate = _patient_state["hr_base"] + random.uniform(-3, 3)
    spo2 = _patient_state["spo2_base"] + random.uniform(-0.5, 0.5)
    respiratory_rate = _patient_state["rr_base"] + random.uniform(-1, 1)

    bp_sys = _patient_state["bp_sys_base"] + random.uniform(-2, 2)
    bp_dia = _patient_state["bp_dia_base"] + random.uniform(-2, 2)

    # Clamp realistic limits
    heart_rate = max(60, min(120, heart_rate))
    spo2 = max(88, min(100, spo2))
    respiratory_rate = max(12, min(28, respiratory_rate))
    bp_sys = max(80, min(200, bp_sys))
    bp_dia = max(50, min(130, bp_dia))

    # ✅ FIXED TIMESTAMP (CRITICAL)
    timestamp = datetime.now(timezone.utc)

    reading = {
        "timestamp": timestamp.isoformat(),  # always UTC ISO
        "heart_rate": int(round(heart_rate)),
        "spo2": int(round(spo2)),
        "respiratory_rate": int(round(respiratory_rate)),
        "blood_pressure_systolic": int(round(bp_sys)),
        "blood_pressure_diastolic": int(round(bp_dia))
    }

    vitals_history.append(reading)
    return reading


def get_history() -> list:
    return list(vitals_history)


def get_latest() -> dict | None:
    return vitals_history[-1] if vitals_history else None