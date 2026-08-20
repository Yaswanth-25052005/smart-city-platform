from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
from backend.domain.sensor import SensorEvent
from backend.services.sensor_service import SensorService

router = APIRouter()

@router.get("/latest", response_model=List[SensorEvent])
def get_latest_sensors(limit: int = Query(10, ge=1, le=100)):
    return SensorService.get_latest(limit)

@router.get("", response_model=List[SensorEvent])
def get_sensors(
    device_id: Optional[str] = None,
    location_id: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0)
):
    if start_time and end_time and start_time > end_time:
        raise HTTPException(status_code=400, detail="start_time must be less than or equal to end_time")
        
    return SensorService.get_sensors(
        device_id=device_id,
        location_id=location_id,
        start_time=start_time,
        end_time=end_time,
        limit=limit,
        offset=offset
    )

@router.get("/device/{device_id}", response_model=List[SensorEvent])
def get_sensors_by_device(
    device_id: str,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0)
):
    return SensorService.get_sensors(device_id=device_id, limit=limit, offset=offset)

@router.get("/location/{location_id}", response_model=List[SensorEvent])
def get_sensors_by_location(
    location_id: str,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0)
):
    return SensorService.get_sensors(location_id=location_id, limit=limit, offset=offset)
