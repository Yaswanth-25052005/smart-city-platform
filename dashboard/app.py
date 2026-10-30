import sys
import os
from pathlib import Path

# Ensure project root is available for robust imports when Streamlit runs pages
project_root = str(Path(__file__).parent.parent.absolute())
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import streamlit as st
import pandas as pd
from dashboard.api import fetch_health, fetch_dashboard_summary, fetch_alerts, fetch_sensors
from dashboard.components import auto_refresh, render_metric_card

st.set_page_config(
    page_title="Smart City Dashboard",
    page_icon="🏙️",
    layout="wide",
)

st.title("🏙️ SMART CITY ANALYTICS PLATFORM")
st.caption("Phase 7 — Real-Time IoT Data & Analytics")

st.sidebar.success("Select a module above.")

auto_refresh(30)

st.header("System Overview")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Platform Health")
    health = fetch_health()
    if health:
        status = health.get("status", "unknown")
        if status == "healthy":
            st.success(f"API status: {status}")
        else:
            st.warning(f"API status: {status}")
        
        st.metric("MongoDB", health.get("mongodb", {}).get("status", "unknown"))
        st.metric("Kafka", health.get("kafka", {}).get("status", "unknown"))
        st.metric("ML Enabled", str(health.get("ml_enabled", False)))
    else:
        st.error("API is unreachable.")

with col2:
    st.subheader("KPIs")
    summary = fetch_dashboard_summary()
    if summary:
        col2_1, col2_2 = st.columns(2)
        with col2_1:
            render_metric_card("Devices", summary.get("device_count", 0))
            render_metric_card("Locations", summary.get("location_count", 0))
            render_metric_card("Total Sensor Events", summary.get("total_sensor_events", 0))
        with col2_2:
            render_metric_card("Active Alerts", summary.get("active_alerts", 0))
            render_metric_card("Critical Alerts", summary.get("critical_alerts", 0))
            
            latest_ts = summary.get("latest_sensor_timestamp")
            if latest_ts:
                try:
                    ts_str = pd.to_datetime(latest_ts).strftime("%Y-%m-%d %H:%M:%S")
                except:
                    ts_str = str(latest_ts)
            else:
                ts_str = "N/A"
            render_metric_card("Latest Update", ts_str)
    else:
        st.warning("Dashboard summary unavailable.")

st.divider()

col3, col4 = st.columns(2)

with col3:
    st.subheader("Recent Alerts")
    alerts = fetch_alerts(status="ACTIVE", limit=5)
    if alerts:
        for alert in alerts:
            severity = alert.get('severity', 'UNKNOWN')
            color = "red" if severity == "CRITICAL" else "orange" if severity == "WARNING" else "blue"
            st.markdown(f"**:{color}[{severity}]** {alert.get('alert_type')} at {alert.get('location_id')}")
    else:
        st.info("No active alerts at this time.")

with col4:
    st.subheader("Latest Sensor Information")
    sensors = fetch_sensors(limit=5)
    if sensors:
        df = pd.DataFrame(sensors)
        display_df = df[['timestamp', 'location_id', 'device_id']].copy()
        if 'temperature' in df.columns:
            display_df['Temp'] = df['temperature'].apply(lambda x: f"{x:.1f}°C" if pd.notnull(x) else "")
        if 'humidity' in df.columns:
            display_df['Hum'] = df['humidity'].apply(lambda x: f"{x:.1f}%" if pd.notnull(x) else "")
        st.dataframe(display_df, use_container_width=True)
    else:
        st.info("No recent sensor data available.")
        