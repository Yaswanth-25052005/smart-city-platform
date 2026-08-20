import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from backend.api.main import app

client = TestClient(app)

mock_analytics_data = [
    {
        "metric": "temperature",
        "location_id": "ZONE_A",
        "date": "2026-08-20",
        "average": 26.5,
        "maximum": 30.1,
        "minimum": 20.0,
        "record_count": 150
    }
]

@patch("backend.services.analytics_service.AnalyticsRepository.find")
def test_get_analytics(mock_find):
    mock_find.return_value = mock_analytics_data
    response = client.get("/api/analytics?metric=temperature&location_id=ZONE_A")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["metric"] == "temperature"
    
    args, kwargs = mock_find.call_args
    assert args[0] == {"metric": "temperature", "location_id": "ZONE_A"}

@patch("backend.services.analytics_service.AnalyticsRepository.find")
def test_get_analytics_by_metric(mock_find):
    mock_find.return_value = mock_analytics_data
    response = client.get("/api/analytics/temperature")
    assert response.status_code == 200
    data = response.json()
    assert data[0]["metric"] == "temperature"
    args, kwargs = mock_find.call_args
    assert args[0] == {"metric": "temperature"}

@patch("backend.services.analytics_service.AnalyticsRepository.find")
def test_get_analytics_by_location(mock_find):
    mock_find.return_value = mock_analytics_data
    response = client.get("/api/analytics/location/ZONE_A")
    assert response.status_code == 200
    data = response.json()
    assert data[0]["location_id"] == "ZONE_A"
    args, kwargs = mock_find.call_args
    assert args[0] == {"location_id": "ZONE_A"}
