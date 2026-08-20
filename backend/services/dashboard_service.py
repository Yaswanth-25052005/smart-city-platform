from backend.database.dashboard_repository import DashboardRepository
from backend.domain.dashboard import DashboardSummary
from typing import Dict, Any

class DashboardService:
    @staticmethod
    def get_summary() -> DashboardSummary:
        total_events = DashboardRepository.get_total_sensor_events()
        active_alerts = DashboardRepository.get_active_alerts_count()
        critical_alerts = DashboardRepository.get_critical_alerts_count()
        device_count = len(DashboardRepository.get_device_ids())
        location_count = len(DashboardRepository.get_location_ids())
        
        latest_event = DashboardRepository.get_latest_sensor_event()
        latest_timestamp = latest_event.get("timestamp") if latest_event else None
        
        # We can extract key metrics globally if needed, but for now we'll keep it simple
        key_metrics: Dict[str, Any] = {}
        
        return DashboardSummary(
            total_sensor_events=total_events,
            active_alerts=active_alerts,
            critical_alerts=critical_alerts,
            device_count=device_count,
            location_count=location_count,
            latest_sensor_timestamp=latest_timestamp,
            key_metrics=key_metrics
        )
