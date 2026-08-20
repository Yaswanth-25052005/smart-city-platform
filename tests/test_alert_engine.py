import pytest
from unittest.mock import patch, MagicMock
from backend.services.alert_engine import AlertEngine
from backend.domain.alert import AlertType

@patch('backend.services.alert_engine.sensor_collection')
@patch('backend.services.alert_engine.analytics_collection')
@patch('backend.services.alert_engine.AlertService')
def test_alert_engine_run(mock_alert_service, mock_analytics_collection, mock_sensor_collection):
    # Mock sensor data
    mock_sensor_collection.find.return_value.sort.return_value.limit.return_value = [
        {"device_id": "DEV1", "location_id": "ZONE_A", "temperature": 50.0, "noise": 60.0},
        {"device_id": "DEV2", "location_id": "ZONE_B", "temperature": 25.0, "noise": 90.0, "streetlight_on": False}
    ]

    # Mock analytics data
    mock_analytics_collection.find.return_value.sort.return_value.limit.return_value = [
        {"location_id": "ZONE_A", "metric": "parking", "average": 0.95},
        {"location_id": "ZONE_B", "metric": "air_quality", "average": 200.0}
    ]

    AlertEngine.run()

    # Assert setup called
    mock_alert_service.setup.assert_called_once()
    
    # Assert condition evaluations
    assert mock_alert_service.evaluate_condition.call_count >= 6
