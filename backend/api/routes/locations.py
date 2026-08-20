from fastapi import APIRouter, HTTPException
from typing import List
from backend.domain.device import LocationInfo
from backend.services.device_service import DeviceService

router = APIRouter()

@router.get("", response_model=List[str])
def get_locations():
    return DeviceService.get_locations()

@router.get("/{location_id}", response_model=LocationInfo)
def get_location(location_id: str):
    loc = DeviceService.get_location(location_id)
    if not loc:
        raise HTTPException(status_code=404, detail="Location not found")
    return loc
