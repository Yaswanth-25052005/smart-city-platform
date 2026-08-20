from backend.database.repository import SensorRepository
from backend.domain.sensor import SensorEvent
from typing import List, Dict, Any, Optional
import uuid

class SensorService:
    @staticmethod
    def map_sensor_doc(doc: Dict[str, Any]) -> SensorEvent:
        if "event_id" not in doc:
            doc["event_id"] = str(uuid.uuid4())
        if "location_id" not in doc:
            doc["location_id"] = "UNKNOWN"
        if "parking" in doc:
            doc["parking_occupied"] = doc.pop("parking")
        if "streetlight" in doc:
            doc["streetlight_on"] = doc.pop("streetlight")
        return SensorEvent(**doc)

    @staticmethod
    def get_latest(limit: int = 10) -> List[SensorEvent]:
        docs = SensorRepository.find_latest(limit)
        return [SensorService.map_sensor_doc(doc) for doc in docs]

    @staticmethod
    def get_sensors(
        device_id: Optional[str] = None,
        location_id: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[SensorEvent]:
        query: Dict[str, Any] = {}
        
        if device_id:
            query["device_id"] = device_id
        if location_id:
            query["location_id"] = location_id
            
        time_query = {}
        if start_time:
            time_query["$gte"] = start_time
        if end_time:
            time_query["$lte"] = end_time
            
        if time_query:
            query["timestamp"] = time_query
            
        docs = SensorRepository.find(query, limit, offset)
        return [SensorService.map_sensor_doc(doc) for doc in docs]
