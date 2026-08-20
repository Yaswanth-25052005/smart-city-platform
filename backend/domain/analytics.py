from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

class AnalyticsResult(BaseModel):
    metric: str
    location_id: str
    date: str
    average: Optional[float] = None
    maximum: Optional[float] = None
    minimum: Optional[float] = None
    record_count: Optional[int] = None
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )
