import streamlit as st
import pandas as pd
import plotly.express as px
from dashboard.api import fetch_analytics
from dashboard.components import auto_refresh, plot_bar

st.set_page_config(page_title="Analytics", page_icon="📊", layout="wide")

st.title("📊 Spark Analytics")
st.caption("Aggregated insights computed via PySpark pipelines.")

auto_refresh(60)

st.sidebar.header("Analytics Filters")
metrics = ["temperature", "humidity", "air_quality", "noise", "parking", "streetlights"]
selected_metric = st.sidebar.selectbox("Select Metric", ["All"] + metrics)

metric_param = None if selected_metric == "All" else selected_metric
analytics = fetch_analytics(metric=metric_param)

if analytics:
    df = pd.DataFrame(analytics)
    
    st.subheader("Analytics Overview")
    st.dataframe(df, use_container_width=True)
    
    # Optional: Basic visualization of averages if available
    if 'average' in df.columns and 'metric' in df.columns:
        valid_avg_df = df.dropna(subset=['average'])
        if not valid_avg_df.empty:
            st.subheader("Average Values by Metric/Location")
            # If multiple metrics, plot average by metric, else by location
            if selected_metric == "All":
                avg_by_metric = valid_avg_df.groupby('metric')['average'].mean().reset_index()
                plot_bar(avg_by_metric, 'metric', 'average', 'Global Averages by Metric', 'metric')
            else:
                plot_bar(valid_avg_df, 'location_id', 'average', f'Average {selected_metric} by Location', 'location_id')
else:
    st.info("No analytics data available for the selected filters.")
