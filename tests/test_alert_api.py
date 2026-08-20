import pytest
from fastapi.testclient import TestClient
from backend.api.main import app
from unittest.mock import patch
from backend.domain.alert import AlertStatus

client = TestClient(app)

@patch('backend.api.routes.alerts.AlertService.get_alerts')
def test_get_alerts(mock_get_alerts):
    mock_get_alerts.return_value = [{"alert_id": "test-123", "status": "ACTIVE"}]
    
    response = client.get("/api/alerts")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["alert_id"] == "test-123"

@patch('backend.api.routes.alerts.AlertService.get_alerts')
def test_get_active_alerts(mock_get_alerts):
    mock_get_alerts.return_value = [{"alert_id": "test-456", "status": "ACTIVE"}]
    
    response = client.get("/api/alerts/active")
    assert response.status_code == 200
    assert len(response.json()) == 1
    # Check that it passed the correct filter
    mock_get_alerts.assert_called_with(status=AlertStatus.ACTIVE.value)

@patch('backend.api.routes.alerts.AlertService.get_alert_by_id')
def test_get_alert_by_id(mock_get_alert):
    mock_get_alert.return_value = {"alert_id": "test-123", "status": "RESOLVED"}
    
    response = client.get("/api/alerts/test-123")
    assert response.status_code == 200
    assert response.json()["status"] == "RESOLVED"

@patch('backend.api.routes.alerts.AlertService.get_alert_by_id')
def test_get_alert_not_found(mock_get_alert):
    mock_get_alert.return_value = None
    
    response = client.get("/api/alerts/invalid-id")
    assert response.status_code == 404
