from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
from backend.domain.analytics import AnalyticsResult
from backend.services.analytics_service import AnalyticsService

router = APIRouter()

@router.get("", response_model=List[AnalyticsResult])
def get_analytics(
    metric: Optional[str] = None,
    location_id: Optional[str] = None,
    date: Optional[str] = None,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0)
):
    return AnalyticsService.get_analytics(
        metric=metric,
        location_id=location_id,
        date=date,
        limit=limit,
        offset=offset
    )

@router.get("/{metric}", response_model=List[AnalyticsResult])
def get_analytics_by_metric(
    metric: str,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0)
):
    return AnalyticsService.get_analytics(metric=metric, limit=limit, offset=offset)

@router.get("/location/{location_id}", response_model=List[AnalyticsResult])
def get_analytics_by_location(
    location_id: str,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0)
):
    return AnalyticsService.get_analytics(location_id=location_id, limit=limit, offset=offset)
