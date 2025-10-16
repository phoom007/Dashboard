# components/mapbox.py
# -*- coding: utf-8 -*-
import streamlit as st
import plotly.express as px
import pandas as pd

def render_thailand_map(df1: pd.DataFrame, df1_melted: pd.DataFrame, th_geojson, selected_month: str, key_prefix="map"):
    st.subheader(f'ยอดขาย OTOP รายจังหวัด • {selected_month}')
    _map_df = df1_melted[df1_melted["เดือน"] == selected_month].dropna(subset=["province_eng"])
    if th_geojson is None or _map_df.empty:
        st.info("ไม่สามารถแสดงแผนที่ได้", icon="ℹ️")
        return

    fig_map = px.choropleth_mapbox(
        _map_df,
        geojson=th_geojson,
        locations="province_eng",
        featureidkey="properties.name",
        color="ยอดขาย",
        color_continuous_scale="Viridis",
        mapbox_style="carto-positron",
        center={"lat": 13.736717, "lon": 100.523186},
        zoom=4.5,
        opacity=0.6,
        hover_name="จังหวัด",
        hover_data={"เดือน": True, "province_eng": False, "ยอดขาย": ":,d"}
    )
    fig_map.update_layout(margin=dict(r=0, t=0, l=0, b=0))
    st.plotly_chart(fig_map, use_container_width=True, config={"displayModeBar": False}, key=f"map_{key_prefix}")
