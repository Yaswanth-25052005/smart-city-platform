import os
import requests
import streamlit as st
from typing import Dict, Any, List, Optional

API_URL = os.getenv("API_URL", "http://localhost:8000").rstrip("/")

def handle_request(method: str, endpoint: str, **kwargs) -> Optional[Any]:
    try:
        response = requests.request(method, f"{API_URL}{endpoint}", timeout=10, **kwargs)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"API Error ({endpoint}): {e}")
        return None

def fetch_health() -> Optional[Dict[str, Any]]:
    return handle_request("GET", "/health")

def fetch_dashboard_summary() -> Optional[Dict[str, Any]]:
    return handle_request("GET", "/api/dashboard/summary")

def fetch_sensors(limit: int = 50, location_id: Optional[str] = None, device_id: Optional[str] = None) -> List[Dict[str, Any]]:
    params = {"limit": limit}
    if location_id:
        params["location_id"] = location_id
    if device_id:
        params["device_id"] = device_id
    res = handle_request("GET", "/api/sensors", params=params)
    return res if res else []

def fetch_alerts(status: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
    params = {}
    if status:
        params["status"] = status
    res = handle_request("GET", "/api/alerts", params=params)
    return res if res else []

def fetch_analytics(metric: Optional[str] = None) -> List[Dict[str, Any]]:
    params = {}
    if metric:
        params["metric"] = metric
    res = handle_request("GET", "/api/analytics", params=params)
    return res if res else []

def fetch_devices() -> List[str]:
    res = handle_request("GET", "/api/devices")
    return res if res else []

def fetch_device_info(device_id: str) -> Optional[Dict[str, Any]]:
    return handle_request("GET", f"/api/devices/{device_id}")

def fetch_locations() -> List[str]:
    res = handle_request("GET", "/api/locations")
    return res if res else []

def fetch_location_info(location_id: str) -> Optional[Dict[str, Any]]:
    return handle_request("GET", f"/api/locations/{location_id}")
