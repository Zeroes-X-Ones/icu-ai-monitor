from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.schemas.vitals_schema import AnalysisResponse
from app.services.vitals_service import VitalsService

router = APIRouter()

@router.get("/", response_model=AnalysisResponse)
def get_window_analysis(window: int = 15, metric: str = None, db: Session = Depends(get_db)):
    """
    Get deep AI analysis over the specified window (in minutes)
    """
    return VitalsService.get_analysis(db, window, metric)
