import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from backend.api.main import app

client = TestClient(app)

@patch("backend.services.dashboard_service.DashboardRepository")
def test_get_dashboard_summary(mock_repo):
    mock_repo.get_total_sensor_events.return_value = 1000
    mock_repo.get_active_alerts_count.return_value = 10
    mock_repo.get_critical_alerts_count.return_value = 2
    mock_repo.get_device_ids.return_value = ["DEV1", "DEV2"]
    mock_repo.get_location_ids.return_value = ["LOC1"]
    mock_repo.get_latest_sensor_event.return_value = {"timestamp": "2026-08-20T10:00:00Z"}
    
    response = client.get("/api/dashboard/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["total_sensor_events"] == 1000
    assert data["active_alerts"] == 10
    assert data["critical_alerts"] == 2
    assert data["device_count"] == 2
    assert data["location_count"] == 1
    assert data["latest_sensor_timestamp"] == "2026-08-20T10:00:00Z"
