import pytest
from pydantic import ValidationError
from datetime import datetime
from backend.domain.alert import AlertModel, AlertType, AlertSeverity, AlertStatus

def test_valid_alert_model():
    alert = AlertModel(
        alert_type=AlertType.HIGH_TEMPERATURE,
        severity=AlertSeverity.HIGH,
        location_id="ZONE_A",
        metric="temperature",
        value=48.5,
        threshold=45.0,
        message="Temp exceeded threshold",
        timestamp=datetime.utcnow()
    )
    assert alert.alert_type == "HIGH_TEMPERATURE"
    assert alert.severity == "HIGH"
    assert alert.status == "ACTIVE"
    assert alert.alert_id is not None

def test_invalid_alert_type():
    with pytest.raises(ValidationError):
        AlertModel(
            alert_type="INVALID_TYPE",
            severity=AlertSeverity.HIGH,
            location_id="ZONE_A",
            metric="temperature",
            value=48.5,
            threshold=45.0,
            message="Temp exceeded threshold",
            timestamp=datetime.utcnow()
        )

def test_invalid_severity():
    with pytest.raises(ValidationError):
        AlertModel(
            alert_type=AlertType.HIGH_TEMPERATURE,
            severity="SUPER_HIGH",
            location_id="ZONE_A",
            metric="temperature",
            value=48.5,
            threshold=45.0,
            message="Temp exceeded threshold",
            timestamp=datetime.utcnow()
        )
