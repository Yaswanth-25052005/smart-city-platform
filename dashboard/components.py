import streamlit as st
import pandas as pd
import plotly.express as px

def render_metric_card(title: str, value: any, delta: any = None):
    st.metric(title, value, delta)

def plot_timeseries(df: pd.DataFrame, x_col: str, y_col: str, title: str, color_col: str = None):
    if df.empty:
        st.info("No data available for plotting.")
        return
    fig = px.line(df, x=x_col, y=y_col, color=color_col, title=title, markers=True)
    st.plotly_chart(fig, use_container_width=True)

def plot_bar(df: pd.DataFrame, x_col: str, y_col: str, title: str, color_col: str = None):
    if df.empty:
        st.info("No data available for plotting.")
        return
    fig = px.bar(df, x=x_col, y=y_col, color=color_col, title=title)
    st.plotly_chart(fig, use_container_width=True)

def auto_refresh(interval_sec: int = 30):
    import time
    if st.button("Refresh Now"):
        st.rerun()
    # Note: Streamlit fragments or st_autorefresh is better, but a manual refresh button + time info is safest to avoid endless looping.
    st.caption(f"Auto-refresh is suggested every {interval_sec} seconds. Click Refresh Now to update.")
