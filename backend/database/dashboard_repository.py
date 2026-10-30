from backend.database.connection import sensor_collection, alerts_collection, analytics_collection
from backend.config.settings import ACTIVE_DEVICES
from typing import Dict, Any, List

class DashboardRepository:
    @staticmethod
    def get_total_sensor_events() -> int:
        return sensor_collection.count_documents({"device_id": {"$in": ACTIVE_DEVICES}})

    @staticmethod
    def get_active_alerts_count() -> int:
        return alerts_collection.count_documents({"status": "ACTIVE", "device_id": {"$in": ACTIVE_DEVICES}})

    @staticmethod
    def get_critical_alerts_count() -> int:
        return alerts_collection.count_documents({"status": "ACTIVE", "severity": "CRITICAL", "device_id": {"$in": ACTIVE_DEVICES}})

    @staticmethod
    def get_device_ids() -> List[str]:
        return ACTIVE_DEVICES

    @staticmethod
    def get_location_ids() -> List[str]:
        return sensor_collection.distinct("location_id", {"device_id": {"$in": ACTIVE_DEVICES}})
    
    @staticmethod
    def get_latest_sensor_event() -> Dict[str, Any]:
        return sensor_collection.find_one({"device_id": {"$in": ACTIVE_DEVICES}}, sort=[("timestamp", -1)])
