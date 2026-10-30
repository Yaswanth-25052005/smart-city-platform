import streamlit as st
import pandas as pd
from dashboard.api import fetch_sensors, fetch_locations
from dashboard.components import auto_refresh, plot_timeseries

st.set_page_config(page_title="Noise Monitoring", page_icon="🔊", layout="wide")

st.title("🔊 Noise Monitoring")
st.caption("City-wide noise levels from acoustic sensors.")

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
        if 'noise' in df.columns and not df['noise'].isnull().all():
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp')
            
            noise_df = df.dropna(subset=['noise'])
            
            curr_noise = noise_df['noise'].iloc[-1]
            avg_noise = noise_df['noise'].mean()
            min_noise = noise_df['noise'].min()
            max_noise = noise_df['noise'].max()
            
            if curr_noise > 80:
                status = "🔴 High Noise"
            elif curr_noise > 60:
                status = "🟠 Elevated"
            else:
                status = "🟢 Normal"
                
            st.subheader(f"Status: {status}")
            
            mc1, mc2, mc3, mc4 = st.columns(4)
            mc1.metric("Current Value", f"{curr_noise:.1f} dB")
            mc2.metric("Average", f"{avg_noise:.1f} dB")
            mc3.metric("Minimum", f"{min_noise:.1f} dB")
            mc4.metric("Maximum", f"{max_noise:.1f} dB")
            
            plot_timeseries(noise_df, 'timestamp', 'noise', 'Noise Level Trend', 'location_id')
        else:
            st.info("No noise data available.")
    else:
        st.warning("No data available.")
