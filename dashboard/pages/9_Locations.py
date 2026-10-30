import streamlit as st
from dashboard.api import fetch_locations, fetch_location_info
from dashboard.components import auto_refresh

st.set_page_config(page_title="Locations View", page_icon="📍", layout="wide")

st.title("📍 Location View")
st.caption("Composite view of all metrics per city location.")

auto_refresh(30)

locations = fetch_locations()

if locations:
    st.write(f"Found {len(locations)} monitored locations.")
    
    # We can create a card or tab for each location, or a selectbox
    selected_loc = st.selectbox("Select Location", locations)
    
    if selected_loc:
        info = fetch_location_info(selected_loc)
        if info:
            st.subheader(f"Location Overview: {selected_loc}")
            
            st.markdown(f"**Active Devices:** {len(info.get('active_devices', []))}")
            st.write(info.get('active_devices', []))
            
            st.markdown("**Latest Aggregated Readings:**")
            readings = info.get('latest_readings', {})
            
            col1, col2, col3, col4 = st.columns(4)
            if 'temperature' in readings:
                col1.metric("Temperature", f"{readings['temperature']:.1f} °C")
            if 'humidity' in readings:
                col2.metric("Humidity", f"{readings['humidity']:.1f} %")
            if 'air_quality' in readings:
                col3.metric("Air Quality", f"{readings['air_quality']:.1f}")
            if 'noise' in readings:
                col4.metric("Noise", f"{readings['noise']:.1f} dB")
                
            st.divider()
            
            col5, col6 = st.columns(2)
            if 'parking_occupied' in readings:
                status = "🔴 Occupied" if readings['parking_occupied'] else "🟢 Available"
                col5.metric("Parking Status", status)
            if 'streetlight_on' in readings:
                status = "🟡 ON" if readings['streetlight_on'] else "⚫ OFF"
                col6.metric("Streetlight Status", status)
        else:
            st.error("Could not fetch location information.")
else:
    st.warning("No locations found.")
