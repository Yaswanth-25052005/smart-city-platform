"""Streamlit dashboard entry point — consumes data via FastAPI only."""

from __future__ import annotations

import os

import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://localhost:8000").rstrip("/")


def fetch_health() -> dict | None:
    try:
        response = requests.get(f"{API_URL}/health", timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        st.error(f"Unable to reach API at {API_URL}: {exc}")
        return None


st.set_page_config(
    page_title="Smart City Dashboard",
    page_icon="🏙️",
    layout="wide",
)

st.title("Smart City Analytics Platform")
st.caption("Phase 1 — Foundation dashboard connected to FastAPI")

st.subheader("Platform Health")
health = fetch_health()

if health:
    status = health.get("status", "unknown")
    if status == "healthy":
        st.success(f"API status: {status}")
    else:
        st.warning(f"API status: {status}")

    col1, col2, col3 = st.columns(3)
    col1.metric("MongoDB", health.get("mongodb", {}).get("status", "unknown"))
    col2.metric("Kafka", health.get("kafka", {}).get("status", "unknown"))
    col3.metric("ML Enabled", str(health.get("ml_enabled", False)))

    with st.expander("Raw health payload"):
        st.json(health)

st.info(
    "Additional dashboard pages (parking, air quality, alerts, predictions) "
    "will be added in later phases."
)
