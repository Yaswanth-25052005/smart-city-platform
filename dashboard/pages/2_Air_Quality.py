import streamlit as st
import pandas as pd
from dashboard.api import fetch_sensors, fetch_locations
from dashboard.components import auto_refresh, plot_timeseries

st.set_page_config(page_title="Air Quality", page_icon="💨", layout="wide")

st.title("💨 Air Quality Monitoring")
st.caption("City-wide air quality metrics from sensor network.")

auto_refresh()

col1, col2 = st.columns([1, 3])

with col1:
    st.subheader("Filters")
    locations = fetch_locations()
    loc_options = ["All"] + locations
    selected_loc = st.selectbox("Location", loc_options)
    limit = st.slider("Recent readings", 10, 500, 100)

with col2:
    loc_param = None if selected_loc == "All" else selected_loc
    sensors = fetch_sensors(limit=limit, location_id=loc_param)
    
    if sensors:
        df = pd.DataFrame(sensors)
        if 'air_quality' in df.columns and not df['air_quality'].isnull().all():
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp')
            
            aq_df = df.dropna(subset=['air_quality'])
            
            curr_aq = aq_df['air_quality'].iloc[-1]
            avg_aq = aq_df['air_quality'].mean()
            min_aq = aq_df['air_quality'].min()
            max_aq = aq_df['air_quality'].max()
            
            # Simple status indicator based on raw metric (not claiming lab-grade AQI)
            if curr_aq > 150:
                status = "🔴 Poor"
            elif curr_aq > 100:
                status = "🟠 Moderate"
            else:
                status = "🟢 Good"
                
            st.subheader(f"Current Status: {status}")
            
            mc1, mc2, mc3, mc4 = st.columns(4)
            mc1.metric("Current Value", f"{curr_aq:.1f}")
            mc2.metric("Average", f"{avg_aq:.1f}")
            mc3.metric("Minimum", f"{min_aq:.1f}")
            mc4.metric("Maximum", f"{max_aq:.1f}")
            
            plot_timeseries(aq_df, 'timestamp', 'air_quality', 'Air Quality Trend', 'location_id')
        else:
            st.info("No air quality data available.")
    else:
        st.warning("No data available.")
