import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from backend.api.main import app

client = TestClient(app)

@patch("backend.services.device_service.DashboardRepository.get_location_ids")
def test_get_locations(mock_get_location_ids):
    mock_get_location_ids.return_value = ["LOC1", "LOC2"]
    response = client.get("/api/locations")
    assert response.status_code == 200
    assert response.json() == ["LOC1", "LOC2"]

@patch("backend.services.device_service.SensorRepository.find")
@patch("backend.services.device_service.sensor_collection.distinct")
def test_get_location(mock_distinct, mock_find):
    mock_find.return_value = [{
        "event_id": "123e4567-e89b-42d3-a456-426614174000",
        "device_id": "DEV1",
        "location_id": "LOC1",
        "timestamp": "2026-08-20T10:00:00Z"
    }]
    mock_distinct.return_value = ["DEV1", "DEV2"]
    
    response = client.get("/api/locations/LOC1")
    assert response.status_code == 200
    data = response.json()
    assert data["location_id"] == "LOC1"
    assert data["device_count"] == 2
    assert data["devices"] == ["DEV1", "DEV2"]

@patch("backend.services.device_service.SensorRepository.find")
def test_get_location_not_found(mock_find):
    mock_find.return_value = []
    response = client.get("/api/locations/UNKNOWN")
    assert response.status_code == 404
    assert response.json()["detail"] == "Location not found"
