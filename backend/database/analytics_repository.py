from backend.database.connection import analytics_collection
from typing import Dict, Any, List

class AnalyticsRepository:
    @staticmethod
    def find(query: Dict[str, Any], limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        return list(
            analytics_collection.find(query, {"_id": 0})
            .sort("date", -1)
            .skip(offset)
            .limit(limit)
        )
