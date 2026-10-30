import streamlit as st
import pandas as pd
from dashboard.api import fetch_sensors, fetch_locations
from dashboard.components import auto_refresh, plot_timeseries

st.set_page_config(page_title="Environment Monitoring", page_icon="🌡️", layout="wide")

st.title("🌡️ Environment Monitoring")
st.caption("Temperature and Humidity across the city.")

auto_refresh()

col1, col2 = st.columns([1, 3])

with col1:
    st.subheader("Filters")
    locations = fetch_locations()
    loc_options = ["All"] + locations
    selected_loc = st.selectbox("Location", loc_options)
    
    limit = st.slider("Number of recent readings", 10, 500, 100)

with col2:
    loc_param = None if selected_loc == "All" else selected_loc
    sensors = fetch_sensors(limit=limit, location_id=loc_param)
    
    if sensors:
        df = pd.DataFrame(sensors)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')
        
        # Temperature
        st.subheader("Temperature (°C)")
        if 'temperature' in df.columns and not df['temperature'].isnull().all():
            temp_df = df.dropna(subset=['temperature'])
            curr_temp = temp_df['temperature'].iloc[-1]
            avg_temp = temp_df['temperature'].mean()
            min_temp = temp_df['temperature'].min()
            max_temp = temp_df['temperature'].max()
            
            mc1, mc2, mc3, mc4 = st.columns(4)
            mc1.metric("Current", f"{curr_temp:.1f} °C")
            mc2.metric("Average", f"{avg_temp:.1f} °C")
            mc3.metric("Minimum", f"{min_temp:.1f} °C")
            mc4.metric("Maximum", f"{max_temp:.1f} °C")
            
            plot_timeseries(temp_df, 'timestamp', 'temperature', 'Temperature Trend', 'location_id')
        else:
            st.info("No temperature data available.")
            
        st.divider()
        
        # Humidity
        st.subheader("Humidity (%)")
        if 'humidity' in df.columns and not df['humidity'].isnull().all():
            hum_df = df.dropna(subset=['humidity'])
            curr_hum = hum_df['humidity'].iloc[-1]
            avg_hum = hum_df['humidity'].mean()
            min_hum = hum_df['humidity'].min()
            max_hum = hum_df['humidity'].max()
            
            mc1, mc2, mc3, mc4 = st.columns(4)
            mc1.metric("Current", f"{curr_hum:.1f} %")
            mc2.metric("Average", f"{avg_hum:.1f} %")
            mc3.metric("Minimum", f"{min_hum:.1f} %")
            mc4.metric("Maximum", f"{max_hum:.1f} %")
            
            plot_timeseries(hum_df, 'timestamp', 'humidity', 'Humidity Trend', 'location_id')
        else:
            st.info("No humidity data available.")
    else:
        st.warning("No sensor data available for the selected filters.")
