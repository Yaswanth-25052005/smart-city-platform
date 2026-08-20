import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from backend.api.main import app

client = TestClient(app)

mock_sensor_data = [
    {
        "event_id": "123e4567-e89b-42d3-a456-426614174000",
        "device_id": "DEVICE_1",
        "location_id": "LOC_1",
        "timestamp": "2026-08-20T10:00:00Z",
        "temperature": 25.5
    },
    {
        "event_id": "123e4567-e89b-42d3-a456-426614174001",
        "device_id": "DEVICE_2",
        "location_id": "LOC_2",
        "timestamp": "2026-08-20T10:01:00Z",
        "humidity": 60.0
    }
]

@patch("backend.services.sensor_service.SensorRepository.find_latest")
def test_get_latest_sensors(mock_find_latest):
    mock_find_latest.return_value = mock_sensor_data
    response = client.get("/api/sensors/latest?limit=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["device_id"] == "DEVICE_1"
    mock_find_latest.assert_called_once_with(2)

@patch("backend.services.sensor_service.SensorRepository.find")
def test_get_sensors_filtered(mock_find):
    mock_find.return_value = [mock_sensor_data[0]]
    response = client.get("/api/sensors?device_id=DEVICE_1&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["device_id"] == "DEVICE_1"
    
    # Check if correct query was passed to find
    args, kwargs = mock_find.call_args
    assert args[0] == {"device_id": "DEVICE_1"}
    assert args[1] == 5 # limit
    assert args[2] == 0 # offset

def test_get_sensors_invalid_dates():
    # start_time > end_time should return 400
    response = client.get("/api/sensors?start_time=2026-08-20T12:00:00Z&end_time=2026-08-20T10:00:00Z")
    assert response.status_code == 400
    assert "start_time must be less than or equal to end_time" in response.json()["detail"]

@patch("backend.services.sensor_service.SensorRepository.find")
def test_get_sensors_by_device(mock_find):
    mock_find.return_value = [mock_sensor_data[0]]
    response = client.get("/api/sensors/device/DEVICE_1")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["device_id"] == "DEVICE_1"

@patch("backend.services.sensor_service.SensorRepository.find")
def test_get_sensors_by_location(mock_find):
    mock_find.return_value = [mock_sensor_data[1]]
    response = client.get("/api/sensors/location/LOC_2")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["location_id"] == "LOC_2"
