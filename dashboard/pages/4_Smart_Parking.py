import streamlit as st
import pandas as pd
from dashboard.api import fetch_sensors, fetch_locations
from dashboard.components import auto_refresh

st.set_page_config(page_title="Smart Parking", page_icon="🅿️", layout="wide")

st.title("🅿️ Smart Parking")
st.caption("Real-time parking space availability and status.")

auto_refresh(15)

st.subheader("City-Wide Parking Overview")

# Fetch latest sensors to determine parking state
# Since parking_occupied is a boolean per event, we can group by device_id to get the latest status
sensors = fetch_sensors(limit=500)

if sensors:
    df = pd.DataFrame(sensors)
    if 'parking_occupied' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')
        
        # Get latest event per location or device that has parking data
        parking_df = df.dropna(subset=['parking_occupied']).copy()
        
        if not parking_df.empty:
            latest_parking = parking_df.groupby('device_id').last().reset_index()
            
            total_spaces = len(latest_parking)
            occupied_spaces = latest_parking['parking_occupied'].sum()
            available_spaces = total_spaces - occupied_spaces
            occupancy_pct = (occupied_spaces / total_spaces) * 100 if total_spaces > 0 else 0
            
            if occupancy_pct >= 90:
                overall_status = "🔴 FULL"
            elif occupancy_pct >= 75:
                overall_status = "🟠 NEARLY FULL"
            elif occupancy_pct >= 50:
                overall_status = "🟡 BUSY"
            else:
                overall_status = "🟢 AVAILABLE"
                
            st.subheader(f"Overall Status: {overall_status}")
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Monitored Spaces", total_spaces)
            col2.metric("Occupied Spaces", int(occupied_spaces))
            col3.metric("Available Spaces", int(available_spaces))
            col4.metric("Occupancy", f"{occupancy_pct:.1f}%")
            
            st.divider()
            st.subheader("Location-wise Parking Status")
            
            # Show table of locations/devices and their parking status
            display_df = latest_parking[['location_id', 'device_id', 'parking_occupied', 'timestamp']].copy()
            display_df['Status'] = display_df['parking_occupied'].apply(lambda x: "🔴 Occupied" if x else "🟢 Available")
            display_df = display_df.drop(columns=['parking_occupied'])
            display_df = display_df.rename(columns={'location_id': 'Location', 'device_id': 'Device ID', 'timestamp': 'Last Updated'})
            
            st.dataframe(display_df, use_container_width=True)
        else:
            st.info("No parking sensor data found in recent events.")
    else:
        st.info("Parking data not available in the current sensor payload.")
else:
    st.warning("No sensor data available.")
