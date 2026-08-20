from fastapi import APIRouter, HTTPException
from typing import List
from backend.domain.device import DeviceInfo
from backend.services.device_service import DeviceService

router = APIRouter()

@router.get("", response_model=List[str])
def get_devices():
    return DeviceService.get_devices()

@router.get("/{device_id}", response_model=DeviceInfo)
def get_device(device_id: str):
    device = DeviceService.get_device(device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return device
