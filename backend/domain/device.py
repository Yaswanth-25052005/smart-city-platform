from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime
from backend.domain.sensor import SensorEvent

class DeviceInfo(BaseModel):
    device_id: str
    location_id: str
    latest_timestamp: Optional[datetime] = None
    latest_status: Optional[SensorEvent] = None
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )

class LocationInfo(BaseModel):
    location_id: str
    device_count: int
    devices: List[str]
    latest_timestamp: Optional[datetime] = None
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )
