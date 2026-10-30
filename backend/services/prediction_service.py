from typing import List, Dict, Any, Optional
from backend.database.prediction_repository import PredictionRepository
from backend.config.settings import ACTIVE_DEVICES

class PredictionService:
    @staticmethod
    def setup():
        PredictionRepository.setup_indexes()

    @staticmethod
    def get_latest_predictions(prediction_type: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        # Enforce ACTIVE_DEVICES filter
        filters = {"device_id": {"$in": ACTIVE_DEVICES}}
        if prediction_type:
            filters["prediction_type"] = prediction_type
            
        return PredictionRepository.find_by_filters(filters, limit)

    @staticmethod
    def get_predictions(
        prediction_type: Optional[str] = None,
        device_id: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        filters = {"device_id": {"$in": ACTIVE_DEVICES}}
        
        if prediction_type:
            filters["prediction_type"] = prediction_type
            
        if device_id and device_id in ACTIVE_DEVICES:
            filters["device_id"] = device_id
            
        return PredictionRepository.find_by_filters(filters, limit)
