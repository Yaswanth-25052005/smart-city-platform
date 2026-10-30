
from pydantic import BaseModel, ConfigDict, UUID4
from typing import Optional
from datetime import datetime


class SensorEvent(BaseModel):
    event_id: UUID4
    device_id: str
    location_id: str
    timestamp: datetime

    # Environmental sensors
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    air_quality: Optional[float] = None
    noise: Optional[float] = None

    # Traffic and smart-city sensors
    ir_detected: Optional[bool] = None
    distance_cm: Optional[float] = None
    vehicle_detected: Optional[bool] = None
    parking_occupied: Optional[bool] = None
    streetlight_on: Optional[bool] = None
    traffic_signal: Optional[str] = None

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        extra="ignore",
    )
