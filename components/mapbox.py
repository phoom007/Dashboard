import streamlit as st
import plotly.express as px
import pandas as pd
from utils.formatters import fmt_baht

def render_thailand_map(df1, df1_melted, thailand_geojson, selected_month, theme_mode="Light"):
    st.markdown("##### แผนที่ยอดขายรายจังหวัด (โทนสีตามมูลค่า, hover มีอันดับ/สัดส่วน)")
    _map_df = df1_melted[df1_melted['เดือน'] == selected_month].dropna(subset=['province_eng']).copy()
    if _map_df.empty or thailand_geojson is None:
        st.info("ไม่สามารถแสดงแผนที่ได้")
        return

    total = _map_df["ยอดขาย"].sum()
    _map_df["share"] = _map_df["ยอดขาย"] / total
    _map_df["rank"] = _map_df["ยอดขาย"].rank(ascending=False, method="min").astype(int)

    fig_map = px.choropleth_mapbox(
        _map_df,
        geojson=thailand_geojson,
        locations='province_eng',
        featureidkey="properties.name",
        color='ยอดขาย',
        color_continuous_scale="Viridis",
        mapbox_style="carto-positron" if theme_mode=="Light" else "carto-darkmatter",
        center={"lat": 13.7367, "lon": 100.5232},
        zoom=4.6,
        opacity=0.65,
        hover_name="province_eng",
        hover_data={
            "ยอดขาย": True,
            "share": lambda s: (s*100).round(2),
            "rank": True,
            "province_eng": False
        }
    )
    fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, height=520)
    st.plotly_chart(fig_map, use_container_width=True)

    # ปุ่มดาวน์โหลด CSV
    csv_bytes = _map_df[["จังหวัด","ยอดขาย","share","rank"]].to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ ดาวน์โหลดข้อมูล CSV ของแผนที่", data=csv_bytes, file_name="map_province_sales.csv", mime="text/csv")
