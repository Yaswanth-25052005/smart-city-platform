import streamlit as st
import pandas as pd
from dashboard.api import fetch_sensors
from dashboard.components import auto_refresh

st.set_page_config(page_title="Street Lighting", page_icon="💡", layout="wide")

st.title("💡 Smart Street Lighting")
st.caption("Monitoring active streetlights and recent status changes.")

auto_refresh(15)

sensors = fetch_sensors(limit=500)

if sensors:
    df = pd.DataFrame(sensors)
    if 'streetlight_on' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')
        
        light_df = df.dropna(subset=['streetlight_on']).copy()
        
        if not light_df.empty:
            latest_lights = light_df.groupby('device_id').last().reset_index()
            
            total_lights = len(latest_lights)
            lights_on = latest_lights['streetlight_on'].sum()
            lights_off = total_lights - lights_on
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Monitored Lights", total_lights)
            col2.metric("Lights ON 🟡", int(lights_on))
            col3.metric("Lights OFF ⚫", int(lights_off))
            
            st.divider()
            st.subheader("Location-wise Status")
            
            display_df = latest_lights[['location_id', 'device_id', 'streetlight_on', 'timestamp']].copy()
            display_df['State'] = display_df['streetlight_on'].apply(lambda x: "🟡 ON" if x else "⚫ OFF")
            display_df = display_df.drop(columns=['streetlight_on'])
            display_df = display_df.rename(columns={'location_id': 'Location', 'device_id': 'Device ID', 'timestamp': 'Last Updated'})
            
            st.dataframe(display_df, use_container_width=True)
            
            # Show recent activity
            st.subheader("Recent Activity / Changes")
            recent = light_df.tail(10)[['timestamp', 'location_id', 'device_id', 'streetlight_on']]
            recent['Action'] = recent['streetlight_on'].apply(lambda x: "Turned ON" if x else "Turned OFF")
            st.table(recent[['timestamp', 'location_id', 'device_id', 'Action']].sort_values('timestamp', ascending=False))
            
        else:
            st.info("No streetlight data found in recent events.")
    else:
        st.info("Streetlight data not available in the current sensor payload.")
else:
    st.warning("No sensor data available.")
