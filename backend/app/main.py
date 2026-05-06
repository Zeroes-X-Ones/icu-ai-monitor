from fastapi import FastAPI
from app.api.v1 import vitals, analysis, websockets
from app.core.database import engine, Base, SessionLocal
from app.core.config import settings
import asyncio
from contextlib import asynccontextmanager
from app.services.vitals_generator import generate_vitals
from app.schemas.vitals_schema import VitalsCreate
from app.services.vitals_service import VitalsService
from app.api.v1.websockets import ws_manager
import json
from datetime import datetime, timedelta, timezone
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables
Base.metadata.create_all(bind=engine)

async def simulate_vitals_loop():
    while True:
        await asyncio.sleep(2)
        try:
            db = SessionLocal()
            vital_dict = generate_vitals()
            vital_in = VitalsCreate(
                heart_rate=vital_dict["heart_rate"],
                spo2=vital_dict["spo2"],
                respiratory_rate=vital_dict.get("respiratory_rate"),
                blood_pressure_systolic=vital_dict["blood_pressure_systolic"],
                blood_pressure_diastolic=vital_dict["blood_pressure_diastolic"]
            )
            db_vital = VitalsService.create_vital(db, vital_in)
            vital_data = {
                "id": db_vital.id,
                "timestamp": db_vital.timestamp.isoformat(),
                "heart_rate": db_vital.heart_rate,
                "spo2": db_vital.spo2,
                "blood_pressure_systolic": db_vital.blood_pressure_systolic,
                "blood_pressure_diastolic": db_vital.blood_pressure_diastolic,
                "alert_level": db_vital.alert_level,
                "ai_summary": db_vital.ai_summary
            }
            await ws_manager.broadcast_vital(json.dumps(vital_data))
        except Exception as e:
            print(f"Error in simulator loop: {e}")
        finally:
            db.close()

# def prepopulate_db():
#     db = SessionLocal()
#     count = db.query(VitalsService.get_vitals.__annotations__.get('return')).count() if hasattr(VitalsService.get_vitals, '__annotations__') else 0
#     # A robust check
#     from app.models.vitals import PatientVitals
#     if db.query(PatientVitals).count() == 0:
#         print("Empty DB detected. Prepopulating 45 minutes of data...")
#         from datetime import datetime, timedelta, timezone
#         now = datetime.now(timezone.utc)
#         # 45 minutes * 60 seconds / 2 seconds = 1350 points
#         for i in range(1350, -1, -1):
#             vital_dict = generate_vitals()
#             vital_in = VitalsCreate(
#                 heart_rate=vital_dict["heart_rate"],
#                 spo2=vital_dict["spo2"],
#                 respiratory_rate=vital_dict.get("respiratory_rate"),
#                 blood_pressure_systolic=vital_dict["blood_pressure_systolic"],
#                 blood_pressure_diastolic=vital_dict["blood_pressure_diastolic"]
#             )
#             # Create without calling realtime AI to save time, or call it? 
#             # We will use the service but override timestamp manually... 
#             # VitalsService uses datetime.now(), so we must patch it or just do it manually.
#             from app.services.ai_engine import AIEngine
#             alert_level, ai_summary = AIEngine.analyze_realtime(vital_in)
#             db_vital = PatientVitals(
#                 heart_rate=vital_in.heart_rate,
#                 spo2=vital_in.spo2,
#                 respiratory_rate=vital_in.respiratory_rate,
#                 blood_pressure_systolic=vital_in.blood_pressure_systolic,
#                 blood_pressure_diastolic=vital_in.blood_pressure_diastolic,
#                 alert_level=alert_level,
#                 ai_summary=ai_summary,
#                 timestamp=now - timedelta(seconds=i*2)
#             )
#             db.add(db_vital)
#             db.flush()
#             from app.models.vitals import Alert
#             ts = now - timedelta(seconds=i*2)
#             if vital_in.heart_rate > 100:
#                 db.add(Alert(timestamp=ts, vital_type="HR", value=vital_in.heart_rate, severity="WARNING" if vital_in.heart_rate < 120 else "CRITICAL", reason="High Heart Rate", vitals_id=db_vital.id))
#             elif vital_in.heart_rate < 60:
#                 db.add(Alert(timestamp=ts, vital_type="HR", value=vital_in.heart_rate, severity="WARNING" if vital_in.heart_rate > 50 else "CRITICAL", reason="Low Heart Rate", vitals_id=db_vital.id))
#             if vital_in.spo2 < 95:
#                 db.add(Alert(timestamp=ts, vital_type="SpO2", value=vital_in.spo2, severity="WARNING" if vital_in.spo2 >= 90 else "CRITICAL", reason="Low Oxygen Saturation", vitals_id=db_vital.id))
#             if vital_in.blood_pressure_systolic > 130 or vital_in.blood_pressure_diastolic > 85:
#                 db.add(Alert(timestamp=ts, vital_type="BP", value=vital_in.blood_pressure_systolic, severity="WARNING" if vital_in.blood_pressure_systolic < 180 else "CRITICAL", reason="High Blood Pressure", vitals_id=db_vital.id))
#             elif vital_in.blood_pressure_systolic < 90 or vital_in.blood_pressure_diastolic < 60:
#                 db.add(Alert(timestamp=ts, vital_type="BP", value=vital_in.blood_pressure_systolic, severity="WARNING" if vital_in.blood_pressure_systolic > 70 else "CRITICAL", reason="Low Blood Pressure", vitals_id=db_vital.id))
#         db.commit()
#         print("Prepopulation complete.")
#     db.close()


from app.models.vitals import PatientVitals, Alert


def prepopulate_db():
    db = SessionLocal()

    # If data already exists, skip
    if db.query(PatientVitals).count() > 0:
        db.close()
        return

    print("Prepopulating 45 minutes of clean history...")

    from datetime import datetime, timedelta, timezone

    # ✅ CORRECT CURRENT TIME BASE
    now = datetime.now(timezone.utc)

    for i in range(1350, -1, -1):
        ts = now - timedelta(seconds=i * 2)

        vital_dict = generate_vitals()

        from app.services.ai_engine import AIEngine
        vital_in = VitalsCreate(
            heart_rate=vital_dict["heart_rate"],
            spo2=vital_dict["spo2"],
            respiratory_rate=vital_dict.get("respiratory_rate"),
            blood_pressure_systolic=vital_dict["blood_pressure_systolic"],
            blood_pressure_diastolic=vital_dict["blood_pressure_diastolic"]
        )

        alert_level, ai_summary = AIEngine.analyze_realtime(vital_in)

        db_vital = PatientVitals(
            heart_rate=vital_in.heart_rate,
            spo2=vital_in.spo2,
            respiratory_rate=vital_in.respiratory_rate,
            blood_pressure_systolic=vital_in.blood_pressure_systolic,
            blood_pressure_diastolic=vital_in.blood_pressure_diastolic,
            alert_level=alert_level,
            ai_summary=ai_summary,
            timestamp=ts  # ✅ aligned timeline
        )

        db.add(db_vital)
        db.flush()

        # Alerts
        if vital_in.heart_rate > 100:
            db.add(Alert(timestamp=ts, vital_type="HR", value=vital_in.heart_rate,
                         severity="WARNING", reason="High HR", vitals_id=db_vital.id))

        if vital_in.spo2 < 95:
            db.add(Alert(timestamp=ts, vital_type="SpO2", value=vital_in.spo2,
                         severity="WARNING", reason="Low SpO2", vitals_id=db_vital.id))

        if vital_in.blood_pressure_systolic > 130:
            db.add(Alert(timestamp=ts, vital_type="BP", value=vital_in.blood_pressure_systolic,
                         severity="WARNING", reason="High BP", vitals_id=db_vital.id))

    db.commit()
    db.close()

    print("History ready.")

@asynccontextmanager
async def lifespan(app: FastAPI):
    prepopulate_db()
    task = asyncio.create_task(simulate_vitals_loop())
    yield
    task.cancel()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Real-time ICU vitals streaming and AI analysis API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS (allow frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, this should be the frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(vitals.router, prefix="/api/v1/vitals", tags=["vitals"])
app.include_router(analysis.router, prefix="/api/v1/analysis", tags=["analysis"])
app.include_router(websockets.router, prefix="/api/v1/ws", tags=["websockets"])

@app.get("/")
def read_root():
    return {"message": "Welcome to AI-Powered Real-Time ICU Monitoring API"}

