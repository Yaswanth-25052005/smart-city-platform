import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from backend.api.main import app

client = TestClient(app)

@patch("backend.services.device_service.DashboardRepository.get_device_ids")
def test_get_devices(mock_get_device_ids):
    mock_get_device_ids.return_value = ["DEV1", "DEV2"]
    response = client.get("/api/devices")
    assert response.status_code == 200
    assert response.json() == ["DEV1", "DEV2"]

@patch("backend.services.device_service.SensorRepository.find")
def test_get_device(mock_find):
    mock_find.return_value = [{
        "event_id": "123e4567-e89b-42d3-a456-426614174000",
        "device_id": "DEV1",
        "location_id": "LOC1",
        "timestamp": "2026-08-20T10:00:00Z",
        "temperature": 22.0
    }]
    response = client.get("/api/devices/DEV1")
    assert response.status_code == 200
    data = response.json()
    assert data["device_id"] == "DEV1"
    assert data["location_id"] == "LOC1"
    assert data["latest_status"]["temperature"] == 22.0

@patch("backend.services.device_service.SensorRepository.find")
def test_get_device_not_found(mock_find):
    mock_find.return_value = []
    response = client.get("/api/devices/UNKNOWN")
    assert response.status_code == 404
    assert response.json()["detail"] == "Device not found"
