# components/mapbox.py
# -*- coding: utf-8 -*-
import streamlit as st
import plotly.express as px

def render_thailand_map(
    df1,
    df1_melted,
    thailand_geojson,          # <- เปลี่ยนชื่อพารามิเตอร์ให้ตรงกับ app.py
    selected_month,
    mapbox_style="carto-positron",
):
    st.subheader(f'ยอดขาย OTOP รายจังหวัด ประจำเดือน {selected_month}')
    _map_df = df1_melted[df1_melted['เดือน'] == selected_month].dropna(subset=['province_eng'])

    if thailand_geojson is not None and not _map_df.empty:
        fig_map = px.choropleth_mapbox(
            _map_df,
            geojson=thailand_geojson,
            locations='province_eng',
            featureidkey="properties.name",
            color='ยอดขาย',
            color_continuous_scale="Viridis",
            mapbox_style=mapbox_style,  # ตามสเปก: แผนที่สว่างตลอด
            center={"lat": 13.736717, "lon": 100.523186},
            zoom=4.5,
            opacity=0.6,
            hover_data={'province_eng': False}
        )
        fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        st.plotly_chart(fig_map, use_container_width=True, config={"displayModeBar": False}, key="thai_map")
    else:
        st.info("ไม่สามารถแสดงแผนที่ได้")
