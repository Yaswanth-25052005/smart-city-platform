from backend.database.connection import prediction_collection
from backend.domain.prediction import PredictionModel
from typing import Dict, Any, List, Optional
import pymongo

class PredictionRepository:
    @staticmethod
    def setup_indexes():
        prediction_collection.create_index([("prediction_id", pymongo.ASCENDING)], unique=True)
        prediction_collection.create_index([("prediction_type", pymongo.ASCENDING)])
        prediction_collection.create_index([("device_id", pymongo.ASCENDING)])
        prediction_collection.create_index([("target_timestamp", pymongo.DESCENDING)])

    @staticmethod
    def insert(prediction: PredictionModel):
        return prediction_collection.insert_one(prediction.model_dump())

    @staticmethod
    def find_latest(prediction_type: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        query = {}
        if prediction_type:
            query["prediction_type"] = prediction_type
            
        return list(
            prediction_collection.find(query, {"_id": 0})
            .sort("target_timestamp", pymongo.DESCENDING)
            .limit(limit)
        )

    @staticmethod
    def find_by_filters(filters: Dict[str, Any], limit: int = 50) -> List[Dict[str, Any]]:
        return list(
            prediction_collection.find(filters, {"_id": 0})
            .sort("target_timestamp", pymongo.DESCENDING)
            .limit(limit)
        )
