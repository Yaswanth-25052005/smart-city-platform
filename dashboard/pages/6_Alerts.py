import streamlit as st
import pandas as pd
from dashboard.api import fetch_alerts
from dashboard.components import auto_refresh

st.set_page_config(page_title="Alert Center", page_icon="🚨", layout="wide")

st.title("🚨 Alert Center")
st.caption("Active and resolved system alerts based on sensor thresholds.")

auto_refresh(15)

col1, col2 = st.columns([1, 3])

with col1:
    st.subheader("Filters")
    status_filter = st.selectbox("Status", ["ACTIVE", "RESOLVED", "ALL"])
    # Not fetching unique alert types here for simplicity, but could be added
    
with col2:
    status_param = None if status_filter == "ALL" else status_filter
    alerts = fetch_alerts(status=status_param, limit=100)
    
    if alerts:
        df = pd.DataFrame(alerts)
        
        active_count = len(df[df['status'] == 'ACTIVE'])
        critical_count = len(df[df['severity'] == 'CRITICAL'])
        
        mc1, mc2 = st.columns(2)
        mc1.metric("Total Shown", len(df))
        mc2.metric("Critical Alerts", critical_count)
        
        # Display alerts in a clean table or cards
        st.subheader("Alert Details")
        
        for _, alert in df.iterrows():
            severity = alert.get('severity', 'UNKNOWN')
            color = "red" if severity == "CRITICAL" else "orange" if severity == "WARNING" else "blue"
            status_icon = "🔔" if alert.get('status') == 'ACTIVE' else "✅"
            
            with st.expander(f"{status_icon} {alert.get('alert_type', 'Alert')} - {alert.get('location_id', 'Unknown Location')}"):
                st.markdown(f"**Severity:** :{color}[{severity}]")
                st.markdown(f"**Device:** {alert.get('device_id')}")
                st.markdown(f"**Metric:** {alert.get('metric')}")
                st.markdown(f"**Trigger Value:** {alert.get('value')} (Threshold: {alert.get('threshold')})")
                st.markdown(f"**Time:** {alert.get('timestamp')}")
                st.markdown(f"**Status:** {alert.get('status')}")
                if alert.get('message'):
                    st.info(alert.get('message'))
    else:
        st.success(f"No {status_filter.lower()} alerts found.")
