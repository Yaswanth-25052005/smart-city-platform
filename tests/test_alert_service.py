import pytest
from unittest.mock import patch
from datetime import datetime, timezone
from backend.domain.alert import AlertType, AlertSeverity, AlertStatus
from backend.services.alert_service import AlertService

@patch('backend.services.alert_service.AlertRepository')
def test_evaluate_condition_new_alert(mock_repo):
    # Setup mock to return no active alert
    mock_repo.find_active_alert.return_value = None
    
    alert = AlertService.evaluate_condition(
        alert_type=AlertType.HIGH_TEMPERATURE,
        severity=AlertSeverity.HIGH,
        location_id="ZONE_A",
        metric="temperature",
        value=48.5,
        threshold=45.0,
        message="Test alert",
        is_abnormal=True,
        device_id="DEV1"
    )
    
    assert alert is not None
    assert alert.alert_type == AlertType.HIGH_TEMPERATURE
    assert alert.status == AlertStatus.ACTIVE
    mock_repo.insert.assert_called_once()

@patch('backend.services.alert_service.AlertRepository')
def test_evaluate_condition_duplicate_prevention(mock_repo):
    # Setup mock to return an existing active alert
    mock_repo.find_active_alert.return_value = {
        "alert_id": "test-uuid",
        "alert_type": "HIGH_TEMPERATURE",
        "status": "ACTIVE"
    }
    
    alert = AlertService.evaluate_condition(
        alert_type=AlertType.HIGH_TEMPERATURE,
        severity=AlertSeverity.HIGH,
        location_id="ZONE_A",
        metric="temperature",
        value=49.0,
        threshold=45.0,
        message="Test alert",
        is_abnormal=True,
        device_id="DEV1"
    )
    
    # Should not create a new alert
    assert alert is None
    mock_repo.insert.assert_not_called()

@patch('backend.services.alert_service.AlertRepository')
def test_evaluate_condition_resolution(mock_repo):
    # Setup mock to return an existing active alert
    mock_repo.find_active_alert.return_value = {
        "alert_id": "test-uuid",
        "alert_type": "HIGH_TEMPERATURE",
        "severity": "HIGH",
        "location_id": "ZONE_A",
        "metric": "temperature",
        "value": 48.5,
        "threshold": 45.0,
        "message": "Test alert",
        "timestamp": datetime.now(timezone.utc),
        "status": "ACTIVE"
    }
    
    # Evaluate with is_abnormal = False (return to normal)
    alert = AlertService.evaluate_condition(
        alert_type=AlertType.HIGH_TEMPERATURE,
        severity=AlertSeverity.HIGH,
        location_id="ZONE_A",
        metric="temperature",
        value=40.0,
        threshold=45.0,
        message="Test alert",
        is_abnormal=False,
        device_id="DEV1"
    )
    
    assert alert is not None
    assert alert.status == AlertStatus.RESOLVED
    mock_repo.update_status.assert_called_once()
