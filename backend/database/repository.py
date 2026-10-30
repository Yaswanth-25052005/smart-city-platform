from backend.database.connection import sensor_collection
from typing import Dict, Any, List

class SensorRepository:

    @staticmethod
    def insert(data):
        return sensor_collection.insert_one(data)

    @staticmethod
    def find_latest(limit: int = 10):
        from backend.config.settings import ACTIVE_DEVICES
        # We sort by timestamp descending instead of _id for accuracy
        return list(
            sensor_collection.find({"device_id": {"$in": ACTIVE_DEVICES}}, {"_id": 0}).sort("timestamp", -1).limit(limit)
        )

    @staticmethod
    def find(query: Dict[str, Any], limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        from backend.config.settings import ACTIVE_DEVICES
        if "device_id" not in query:
            query["device_id"] = {"$in": ACTIVE_DEVICES}
        return list(
            sensor_collection.find(query, {"_id": 0})
            .sort("timestamp", -1)
            .skip(offset)
            .limit(limit)
        )

    @staticmethod
    def delete_all():
        sensor_collection.delete_many({})