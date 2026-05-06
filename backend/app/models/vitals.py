from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.database import Base

class PatientVitals(Base):
    __tablename__ = "patient_vitals"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    heart_rate = Column(Float, nullable=False)
    spo2 = Column(Float, nullable=False)
    blood_pressure_systolic = Column(Integer, nullable=False)
    blood_pressure_diastolic = Column(Integer, nullable=False)
    respiratory_rate = Column(Float, nullable=True)
    alert_level = Column(String, default="INFO")
    ai_summary = Column(String, default="")


    alerts = relationship("Alert", back_populates="vital_record", cascade="all, delete-orphan")

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    vital_type = Column(String, nullable=False) # HR, SpO2, BP, RR
    value = Column(Float, nullable=False)
    severity = Column(String, nullable=False) # NORMAL, WARNING, CRITICAL
    reason = Column(String, nullable=False)
    vitals_id = Column(Integer, ForeignKey("patient_vitals.id"))

    vital_record = relationship("PatientVitals", back_populates="alerts")
