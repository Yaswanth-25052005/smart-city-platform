from backend.database.connection import sensor_collection, alerts_collection, analytics_collection
from typing import Dict, Any, List

class DashboardRepository:
    @staticmethod
    def get_total_sensor_events() -> int:
        return sensor_collection.estimated_document_count()

    @staticmethod
    def get_active_alerts_count() -> int:
        return alerts_collection.count_documents({"status": "ACTIVE"})

    @staticmethod
    def get_critical_alerts_count() -> int:
        return alerts_collection.count_documents({"status": "ACTIVE", "severity": "CRITICAL"})

    @staticmethod
    def get_device_ids() -> List[str]:
        return sensor_collection.distinct("device_id")

    @staticmethod
    def get_location_ids() -> List[str]:
        return sensor_collection.distinct("location_id")
    
    @staticmethod
    def get_latest_sensor_event() -> Dict[str, Any]:
        return sensor_collection.find_one({}, sort=[("timestamp", -1)])
