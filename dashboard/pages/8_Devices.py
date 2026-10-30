import streamlit as st
from dashboard.api import fetch_devices, fetch_device_info
from dashboard.components import auto_refresh

st.set_page_config(page_title="Device Monitoring", page_icon="📱", layout="wide")

st.title("📱 Device Monitoring")
st.caption("Status of active IoT sensor nodes.")

auto_refresh(30)

devices = fetch_devices()

if devices:
    st.write(f"Found {len(devices)} active devices.")
    
    selected_device = st.selectbox("Select a Device to inspect", devices)
    
    if selected_device:
        info = fetch_device_info(selected_device)
        if info:
            st.subheader(f"Device Details: {selected_device}")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**Location ID:** {info.get('location_id', 'Unknown')}")
                st.markdown(f"**Status:** 🟢 Active")
                st.markdown(f"**Last Seen:** {info.get('last_seen', 'Unknown')}")
                
            with col2:
                st.markdown("**Latest Readings:**")
                st.json(info.get('latest_readings', {}))
        else:
            st.error("Could not fetch device information.")
else:
    st.warning("No devices found.")
