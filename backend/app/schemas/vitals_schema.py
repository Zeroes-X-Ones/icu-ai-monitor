from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class VitalsCreate(BaseModel):
    heart_rate: float
    spo2: float
    blood_pressure_systolic: int
    blood_pressure_diastolic: int
    respiratory_rate: Optional[float] = None

class VitalsResponse(VitalsCreate):
    id: int
    timestamp: datetime
    alert_level: str
    ai_summary: str
    
    model_config = ConfigDict(from_attributes=True)

class AlertResponse(BaseModel):
    id: int
    timestamp: datetime
    vital_type: str
    value: float
    severity: str
    reason: str
    vitals_id: int
    
    model_config = ConfigDict(from_attributes=True)

from typing import Dict, List, Any

class MetricAnalysis(BaseModel):
    avg: float
    min: float
    max: float
    abnormal_frequency: int
    trend: str
    spikes_drops: int

class ClinicalEvent(BaseModel):
    timestamp: str
    type: str
    severity: str
    description: str
    priority: int

class ClinicalRecommendation(BaseModel):
    condition: str
    action: str
    text: str = "" # New field for Phase 2
    priority: Any # Can be int or str for compatibility

class TimelineEvent(BaseModel):
    timestamp: str
    event: str

class VitalsForecast(BaseModel):
    spo2: float = 97.0
    heart_rate: float = 75.0
    bp_sys: float = 120.0
    respiratory_rate: float = 16.0

class AnalysisResponse(BaseModel):
    window_minutes: int
    key_observation: str
    risk_level: str
    distress_score: int = 0
    condition: str = "Stable"
    trend: str
    events: List[ClinicalEvent] = []
    recommendations: List[ClinicalRecommendation] = []
    timeline: List[TimelineEvent] = []
    prediction: str
    prediction_confidence: float = 0.0
    possible_cause: str
    metrics: Dict[str, MetricAnalysis]
    confidence_score: float
    alert_explanation: str = ""
    # -- ML-enhanced fields (Phase 3) ------------------------------
    ml_prediction: str = ""          # ML model's raw risk prediction
    ml_confidence: float = 0.0       # ML model's confidence (0-1)
    explainability: str = ""          # human-readable top-feature description
    # -- Time-series forecast fields (Phase 4) ---------------------
    vitals_forecast: Optional[VitalsForecast] = None  # predicted vitals
    forecast_risk: str = ""           # risk prediction summary
    forecast_confidence: float = 0.0  # forecast confidence (0-1)
    forecast_explanation: str = ""     # explainable forecast reasoning
    # -- Anomaly detection fields (Phase 5) ------------------------
    anomalies: List[Any] = []        # per-signal Z-score anomalies
    patterns: Optional[Any] = None   # recurrent pattern data
    baseline: Optional[Any] = None   # patient-specific baseline stats
    # -- LLM clinical reasoning (Phase 6) -------------------------
    llm_summary: Optional[Any] = None  # LLM-generated clinical reasoning

    model_config = ConfigDict(extra="allow")
