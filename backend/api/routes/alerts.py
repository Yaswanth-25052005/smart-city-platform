from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
from backend.services.alert_service import AlertService
from backend.domain.alert import AlertStatus

router = APIRouter()

@router.get("", response_model=List[Dict[str, Any]])
def get_alerts(
    status: Optional[str] = Query(None, description="Filter by status (ACTIVE/RESOLVED)"),
    alert_type: Optional[str] = Query(None, description="Filter by alert type"),
    location_id: Optional[str] = Query(None, description="Filter by location_id"),
    severity: Optional[str] = Query(None, description="Filter by severity")
):
    try:
        return AlertService.get_alerts(
            status=status, 
            alert_type=alert_type, 
            location_id=location_id, 
            severity=severity
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/active", response_model=List[Dict[str, Any]])
def get_active_alerts():
    try:
        return AlertService.get_alerts(status=AlertStatus.ACTIVE.value)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/location/{location_id}", response_model=List[Dict[str, Any]])
def get_alerts_by_location(location_id: str):
    try:
        return AlertService.get_alerts(location_id=location_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{alert_id}", response_model=Dict[str, Any])
def get_alert(alert_id: str):
    try:
        alert = AlertService.get_alert_by_id(alert_id)
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        return alert
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
