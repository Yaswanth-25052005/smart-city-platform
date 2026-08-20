from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
from datetime import datetime
import uuid

class AlertType(str, Enum):
    AIR_QUALITY = "AIR_QUALITY"
    HIGH_TEMPERATURE = "HIGH_TEMPERATURE"
    HIGH_NOISE = "HIGH_NOISE"
    PARKING_CONGESTION = "PARKING_CONGESTION"
    STREETLIGHT_ANOMALY = "STREETLIGHT_ANOMALY"
    DATA_QUALITY = "DATA_QUALITY"

class AlertSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class AlertStatus(str, Enum):
    ACTIVE = "ACTIVE"
    RESOLVED = "RESOLVED"

class AlertModel(BaseModel):
    alert_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    alert_type: AlertType
    severity: AlertSeverity
    device_id: Optional[str] = None
    location_id: str
    metric: str
    value: float
    threshold: float
    message: str
    timestamp: datetime
    status: AlertStatus = AlertStatus.ACTIVE

    class Config:
        use_enum_values = True
