from backend.database.analytics_repository import AnalyticsRepository
from backend.domain.analytics import AnalyticsResult
from typing import List, Dict, Any, Optional

class AnalyticsService:
    @staticmethod
    def get_analytics(
        metric: Optional[str] = None,
        location_id: Optional[str] = None,
        date: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[AnalyticsResult]:
        query: Dict[str, Any] = {}
        
        if metric:
            query["metric"] = metric
        if location_id:
            query["location_id"] = location_id
        if date:
            # Simple string match, spark generates ISO dates usually
            query["date"] = date
            
        docs = AnalyticsRepository.find(query, limit, offset)
        return [AnalyticsResult(**doc) for doc in docs]
