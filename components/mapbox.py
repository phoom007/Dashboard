# components/mapbox.py
import streamlit as st
import plotly.express as px
import pandas as pd

def render_thailand_map(df1, df1_melted, thailand_geojson, selected_month):
    st.markdown("##### แผนที่ยอดขายรายจังหวัด (โทนสีตามมูลค่า, hover มีอันดับ/สัดส่วน)")
    _map_df = df1_melted[df1_melted['เดือน'] == selected_month].dropna(subset=['province_eng']).copy()
    if _map_df.empty or thailand_geojson is None:
        st.info("ไม่สามารถแสดงแผนที่ได้")
        return

    total = float(_map_df["ยอดขาย"].sum()) or 1.0
    _map_df["ยอดขาย (บาท)"] = _map_df["ยอดขาย"]
    _map_df["สัดส่วน (%)"]   = (_map_df["ยอดขาย"] / total) * 100.0
    _map_df["อันดับ"]        = _map_df["ยอดขาย"].rank(ascending=False, method="min").astype(int)

    fig_map = px.choropleth_mapbox(
        _map_df,
        geojson=thailand_geojson,
        locations='province_eng',
        featureidkey="properties.name",
        color='ยอดขาย',
        color_continuous_scale="Viridis",
        mapbox_style="carto-positron",   # สว่างตลอด
        center={"lat": 13.7367, "lon":
