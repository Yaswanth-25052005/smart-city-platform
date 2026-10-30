from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from backend.domain.alert import AlertModel, AlertType, AlertSeverity, AlertStatus
from backend.database.alert_repository import AlertRepository

class AlertService:
    @staticmethod
    def setup():
        AlertRepository.setup_indexes()

    @staticmethod
    def evaluate_condition(
        alert_type: AlertType,
        severity: AlertSeverity,
        location_id: str,
        metric: str,
        value: float,
        threshold: float,
        message: str,
        is_abnormal: bool,
        device_id: Optional[str] = None
    ) -> Optional[AlertModel]:
        """
        Evaluates a condition and manages deduplication and resolution.
        """
        active_alert_doc = AlertRepository.find_active_alert(
            alert_type=alert_type.value,
            location_id=location_id,
            device_id=device_id
        )

        now = datetime.now(timezone.utc)

        if is_abnormal:
            if not active_alert_doc:
                # Create NEW ACTIVE alert
                new_alert = AlertModel(
                    alert_type=alert_type,
                    severity=severity,
                    device_id=device_id,
                    location_id=location_id,
                    metric=metric,
                    value=value,
                    threshold=threshold,
                    message=message,
                    timestamp=now
                )
                AlertRepository.insert(new_alert)
                return new_alert
            # else: Condition continues, DO NOT create duplicate
            return None
        else:
            if active_alert_doc:
                # Condition returns to normal -> RESOLVE
                AlertRepository.update_status(
                    alert_id=active_alert_doc["alert_id"],
                    status=AlertStatus.RESOLVED.value,
                    timestamp=now.isoformat()
                )
                # We return the resolved alert representation
                resolved_alert = AlertModel(**active_alert_doc)
                resolved_alert.status = AlertStatus.RESOLVED
                resolved_alert.timestamp = now
                return resolved_alert
            # else: normal condition, no active alert to resolve
            return None

    @staticmethod
    def get_alerts(
        status: Optional[str] = None,
        alert_type: Optional[str] = None,
        location_id: Optional[str] = None,
        severity: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        from backend.config.settings import ACTIVE_DEVICES
        filters = {"device_id": {"$in": ACTIVE_DEVICES}}
        if status:
            filters["status"] = status
        if alert_type:
            filters["alert_type"] = alert_type
        if location_id:
            filters["location_id"] = location_id
        if severity:
            filters["severity"] = severity
            
        return AlertRepository.find_by_filters(filters)

    @staticmethod
    def get_alert_by_id(alert_id: str) -> Optional[Dict[str, Any]]:
        return AlertRepository.find_by_id(alert_id)
