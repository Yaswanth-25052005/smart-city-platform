from backend.database.connection import sensor_collection
from typing import Dict, Any, List

class SensorRepository:

    @staticmethod
    def insert(data):
        return sensor_collection.insert_one(data)

    @staticmethod
    def find_latest(limit: int = 10):
        # We sort by timestamp descending instead of _id for accuracy
        return list(
            sensor_collection.find({}, {"_id": 0}).sort("timestamp", -1).limit(limit)
        )

    @staticmethod
    def find(query: Dict[str, Any], limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        return list(
            sensor_collection.find(query, {"_id": 0})
            .sort("timestamp", -1)
            .skip(offset)
            .limit(limit)
        )

    @staticmethod
    def delete_all():
        sensor_collection.delete_many({})