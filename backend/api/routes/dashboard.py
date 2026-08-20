from fastapi import APIRouter
from backend.domain.dashboard import DashboardSummary
from backend.services.dashboard_service import DashboardService

router = APIRouter()

@router.get("/summary", response_model=DashboardSummary)
def get_dashboard_summary():
    return DashboardService.get_summary()
