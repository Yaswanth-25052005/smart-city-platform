import pytest
from backend.config.settings import ACTIVE_DEVICES
from backend.database.dashboard_repository import DashboardRepository
from backend.database.repository import SensorRepository
from backend.services.alert_service import AlertService
from unittest.mock import patch, MagicMock

def test_active_devices_config():
    assert len(ACTIVE_DEVICES) == 2
    assert "ESP32_ENV_01" in ACTIVE_DEVICES
    assert "ESP32_TRAFFIC_01" in ACTIVE_DEVICES
    assert "ESP32_01" not in ACTIVE_DEVICES
    assert "ESP32_02" not in ACTIVE_DEVICES
    assert "ESP32_03" not in ACTIVE_DEVICES
    assert "ESP32_04" not in ACTIVE_DEVICES
    assert "ESP32_05" not in ACTIVE_DEVICES

def test_dashboard_repository_devices():
    devices = DashboardRepository.get_device_ids()
    assert devices == ACTIVE_DEVICES
    assert len(devices) == 2

@patch("backend.database.repository.sensor_collection")
def test_sensor_repository_filters_by_active_devices(mock_sensor_collection):
    mock_cursor = MagicMock()
    mock_cursor.sort.return_value = mock_cursor
    mock_cursor.limit.return_value = []
    mock_cursor.skip.return_value = mock_cursor
    
    mock_sensor_collection.find.return_value = mock_cursor
    
    # Test find_latest
    SensorRepository.find_latest(10)
    mock_sensor_collection.find.assert_called_with({"device_id": {"$in": ACTIVE_DEVICES}}, {"_id": 0})
    
    # Test find without device_id
    SensorRepository.find({})
    mock_sensor_collection.find.assert_called_with({"device_id": {"$in": ACTIVE_DEVICES}}, {"_id": 0})

@patch("backend.services.alert_service.AlertRepository")
def test_alert_service_filters_by_active_devices(mock_alert_repo):
    mock_alert_repo.find_by_filters.return_value = []
    
    AlertService.get_alerts()
    mock_alert_repo.find_by_filters.assert_called_with({"device_id": {"$in": ACTIVE_DEVICES}})
