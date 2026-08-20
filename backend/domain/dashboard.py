from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime

class DashboardSummary(BaseModel):
    total_sensor_events: int
    active_alerts: int
    critical_alerts: int
    device_count: int
    location_count: int
    latest_sensor_timestamp: Optional[datetime] = None
    key_metrics: Optional[Dict[str, Any]] = None
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )
