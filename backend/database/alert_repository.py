from backend.database.connection import alerts_collection
from backend.domain.alert import AlertModel, AlertStatus
import pymongo
from typing import List, Dict, Any, Optional

class AlertRepository:

    @staticmethod
    def setup_indexes():
        alerts_collection.create_index([("alert_id", pymongo.ASCENDING)], unique=True)
        alerts_collection.create_index([("alert_type", pymongo.ASCENDING)])
        alerts_collection.create_index([("location_id", pymongo.ASCENDING)])
        alerts_collection.create_index([("status", pymongo.ASCENDING)])
        alerts_collection.create_index([("timestamp", pymongo.DESCENDING)])
    
    @staticmethod
    def insert(alert: AlertModel):
        return alerts_collection.insert_one(alert.dict())
    
    @staticmethod
    def find_active_alert(alert_type: str, location_id: str, device_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        query = {
            "alert_type": alert_type,
            "location_id": location_id,
            "status": AlertStatus.ACTIVE.value
        }
        if device_id:
            query["device_id"] = device_id
            
        return alerts_collection.find_one(query)

    @staticmethod
    def update_status(alert_id: str, status: str, timestamp: str):
        return alerts_collection.update_one(
            {"alert_id": alert_id},
            {"$set": {"status": status, "timestamp": timestamp}}
        )

    @staticmethod
    def find_by_filters(filters: Dict[str, Any], limit: int = 100) -> List[Dict[str, Any]]:
        return list(alerts_collection.find(filters, {"_id": 0}).sort("timestamp", pymongo.DESCENDING).limit(limit))

    @staticmethod
    def find_by_id(alert_id: str) -> Optional[Dict[str, Any]]:
        return alerts_collection.find_one({"alert_id": alert_id}, {"_id": 0})
    
    @staticmethod
    def delete_all():
        alerts_collection.delete_many({})
