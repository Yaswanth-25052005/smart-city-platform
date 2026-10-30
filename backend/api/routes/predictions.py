from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
from backend.services.prediction_service import PredictionService

router = APIRouter(prefix="/api/predictions", tags=["Predictions"])

@router.get("", response_model=List[Dict[str, Any]])
def get_predictions(
    type: Optional[str] = Query(None, description="prediction_type filter (e.g. parking, air_quality)"),
    device_id: Optional[str] = Query(None, description="device_id filter"),
    limit: int = Query(50, ge=1, le=1000)
):
    try:
        return PredictionService.get_predictions(
            prediction_type=type,
            device_id=device_id,
            limit=limit
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/latest", response_model=List[Dict[str, Any]])
def get_latest_predictions(
    type: Optional[str] = Query(None, description="prediction_type filter"),
    limit: int = Query(10, ge=1, le=100)
):
    try:
        return PredictionService.get_latest_predictions(
            prediction_type=type,
            limit=limit
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
