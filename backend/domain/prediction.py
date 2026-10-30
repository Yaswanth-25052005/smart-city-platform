from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime

class PredictionModel(BaseModel):
    prediction_id: str
    prediction_type: str
    device_id: str
    location_id: str
    target_timestamp: datetime
    predicted_value: float
    model_version: str
    evaluation_metrics: Optional[Dict[str, Any]] = None
    created_at: datetime
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )
