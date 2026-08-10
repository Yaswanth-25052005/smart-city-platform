from pydantic import BaseModel, Field, ConfigDict, UUID4
from typing import Optional
from datetime import datetime

class SensorEvent(BaseModel):
    event_id: UUID4
    device_id: str
    location_id: str
    timestamp: datetime
    
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    air_quality: Optional[float] = None
    noise: Optional[float] = None
    
    parking_occupied: Optional[bool] = None
    streetlight_on: Optional[bool] = None
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )
