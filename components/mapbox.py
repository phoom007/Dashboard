# components/mapbox.py  (เวอร์ชันแก้ error Ambiguous input)
import streamlit as st
import plotly.express as px
import pandas as pd

def render_thailand_map(df1, df1_melted, thailand_geojson, selected_month, theme_mode="Light"):
    st.markdown("##### แผนที่ยอดขายรายจังหวัด (โทนสีตามมูลค่า, hover มีอันดับ/สัดส่วน)")
    _map_df = df1_melted[df1_melted['เดือน'] == selected_month].dropna(subset=['province_eng']).copy()
    if _map_df.empty or thailand_geojson is None:
        st.info("ไม่สามารถแสดงแผนที่ได้")
        return

    total = float(_map_df["ยอดขาย"].sum()) or 1.0

    # สร้างคอลัมน์ใหม่เพื่อใช้ใน hover (หลีกเลี่ยงชื่อซ้ำกับคอลัมน์จริง)
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
        center={"lat": 13.7367, "lon": 100.5232},
        zoom=4.6,
        opacity=0.65,
        hover_name="จังหวัด",
        hover_data={
            "ยอดขาย (บาท)": ':.0f',
            "สัดส่วน (%)": ':.2f',
            "อันดับ": True
        }
    )
    fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, height=520)
    st.plotly_chart(fig_map, use_container_width=True)

    # ปุ่มดาวน์โหลด CSV ของข้อมูลที่ใช้ในแผนที่
    csv_bytes = _map_df[["จังหวัด","ยอดขาย (บาท)","สัดส่วน (%)","อันดับ"]].to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ ดาวน์โหลดข้อมูล CSV ของแผนที่",
                       data=csv_bytes,
                       file_name="map_province_sales.csv",
                       mime="text/csv")

