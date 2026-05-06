# from fastapi import APIRouter, Depends
# from sqlalchemy.orm import Session
# from typing import List
# from app.api.deps import get_db
# from app.schemas.vitals_schema import VitalsCreate, VitalsResponse, AlertResponse
# from app.services.vitals_service import VitalsService

# # Need this to broadcast the new vital
# # We will import the ws_manager directly
# from app.api.v1.websockets import ws_manager

# router = APIRouter()

# @router.post("/", response_model=VitalsResponse)
# async def create_vital(vital_in: VitalsCreate, db: Session = Depends(get_db)):
#     db_vital = VitalsService.create_vital(db, vital_in)
    
#     # Broadcast to all websocket connections
#     vital_data = {
#         "id": db_vital.id,
#         "timestamp": db_vital.timestamp.isoformat(),
#         "heart_rate": db_vital.heart_rate,
#         "spo2": db_vital.spo2,
#         "blood_pressure_systolic": db_vital.blood_pressure_systolic,
#         "blood_pressure_diastolic": db_vital.blood_pressure_diastolic,
#         "alert_level": db_vital.alert_level,
#         "ai_summary": db_vital.ai_summary
#     }
#     # It's an async call so we must await it, hence the async def router route above
#     import json
#     await ws_manager.broadcast_vital(json.dumps(vital_data))
    
#     return db_vital

# @router.get("/", response_model=List[VitalsResponse])
# def read_vitals(limit: int = 100, minutes: int = None, db: Session = Depends(get_db)):
#     # Cap limit to 2000 for safety if minutes is provided
#     if minutes and limit == 100:
#         limit = 2000
#     return VitalsService.get_vitals(db, limit, minutes)

# @router.get("/alerts", response_model=List[AlertResponse])
# def read_alerts(limit: int = 50, db: Session = Depends(get_db)):
#     return VitalsService.get_alerts(db, limit)
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.api.deps import get_db
from app.schemas.vitals_schema import VitalsCreate, VitalsResponse, AlertResponse
from app.services.vitals_service import VitalsService
from app.models.vitals import PatientVitals
from app.api.v1.websockets import ws_manager

router = APIRouter()


# ✅ CREATE + BROADCAST
@router.post("/", response_model=VitalsResponse)
async def create_vital(vital_in: VitalsCreate, db: Session = Depends(get_db)):
    db_vital = VitalsService.create_vital(db, vital_in)

    import json
    await ws_manager.broadcast_vital(json.dumps({
        "id": db_vital.id,
        "timestamp": db_vital.timestamp.isoformat(),
        "heart_rate": db_vital.heart_rate,
        "spo2": db_vital.spo2,
        "blood_pressure_systolic": db_vital.blood_pressure_systolic,
        "blood_pressure_diastolic": db_vital.blood_pressure_diastolic,
        "alert_level": db_vital.alert_level,
        "ai_summary": db_vital.ai_summary
    }))

    return db_vital


# ✅ HISTORY (FIXED)
@router.get("/history")
def get_vitals_history(minutes: int = 60, db: Session = Depends(get_db)):
    vitals = VitalsService.get_vitals(db, minutes=minutes)

    return {
        "history": [
            {
                "timestamp": v.timestamp.isoformat(),
                "heart_rate": v.heart_rate,
                "spo2": v.spo2,
                "respiratory_rate": v.respiratory_rate,
                "blood_pressure_systolic": v.blood_pressure_systolic,
                "blood_pressure_diastolic": v.blood_pressure_diastolic,
                "alert_level": v.alert_level,
                "ai_summary": v.ai_summary,
            }
            for v in vitals
        ]
    }


# ✅ LATEST
@router.get("/latest")
def get_latest_vitals(db: Session = Depends(get_db)):
    latest = (
        db.query(PatientVitals)
        .order_by(PatientVitals.timestamp.desc())
        .first()
    )

    if not latest:
        return {}

    return {
        "timestamp": latest.timestamp.isoformat(),
        "heart_rate": latest.heart_rate,
        "spo2": latest.spo2,
        "respiratory_rate": latest.respiratory_rate,
        "blood_pressure_systolic": latest.blood_pressure_systolic,
        "blood_pressure_diastolic": latest.blood_pressure_diastolic,
        "alert_level": latest.alert_level,
        "ai_summary": latest.ai_summary,
    }


# ✅ SESSION START
@router.get("/session-start")
def get_session_start(db: Session = Depends(get_db)):
    first = (
        db.query(PatientVitals)
        .order_by(PatientVitals.timestamp.asc())
        .first()
    )

    if not first:
        return {"start": None}

    return {"start": first.timestamp.isoformat()}


# ✅ ALERTS (keep existing)
@router.get("/alerts", response_model=List[AlertResponse])
def read_alerts(limit: int = 50, db: Session = Depends(get_db)):
    return VitalsService.get_alerts(db, limit)