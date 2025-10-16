# app.py
# -*- coding: utf-8 -*-
import traceback
import streamlit as st

from utils.theme import set_base_page_config, inject_global_css, get_plotly_template
from utils.data import load_all_data, load_geojson
from components.header import render_header
from components.sidebar import render_sidebar
from components.kpi_card import render_kpis
from components.mapbox import render_thailand_map
from components.charts import (
    render_main_row_charts,
    render_revenue_sources,
    render_cdd_sources_embeds,
)


def main():
    # Theme & page
    set_base_page_config()
    inject_global_css()

    # Header Night/Day toggle
    render_header()

    # Data
    df1, df2, df3, df1_melted, national_avg, month_cols = load_all_data()
    th_geo = load_geojson()

    # Sidebar
    sb = render_sidebar(df1, df2, df3)
    selected_month = sb["selected_month"]
    selected_province = sb["selected_province"]

    # Title
    st.title("🛍️ Dashboard สรุปผลการจำหน่ายสินค้า OTOP (ชุดเติบโต)")
    st.caption(
        f"ข้อมูลประจำเดือน **{selected_month}** • หน่วยเป็นบาท (฿) • "
        "แหล่งข้อมูล: otop_r04, otop_r05, otop_r06 (ดูท้ายหน้า)"
    )

    # KPI
    render_kpis(df1, df2, df3, selected_month)
    st.markdown("")

    # Main charts (ย่อ)
    try:
        render_main_row_charts(
            df1, df2, selected_month,
            month_cols=month_cols,
            selected_province=selected_province,
            plotly_template=get_plotly_template(),
            key_prefix="main",
        )
    except TypeError:
        # เผื่อซิกเนเจอร์เดิมในโปรเจกต์อื่น
        render_main_row_charts(df1, df2, selected_month, plotly_template=get_plotly_template())

    st.markdown("---")

    # Tabs
    tab1, tab2 = st.tabs(["🗺️ ภาพรวมรายจังหวัด", "🔎 วิเคราะห์เชิงลึก"])

    with tab1:
        # Map — รองรับทั้งชื่อพารามิเตอร์ใหม่/เก่า
        try:
            render_thailand_map(df1, df1_melted, th_geo, selected_month)
        except TypeError:
            render_thailand_map(
                df1=df1, df1_melted=df1_melted, thailand_geojson=th_geo, selected_month=selected_month
            )

        # Revenue Sources (เดือนเดียว) — แสดงในทั้ง 2 แท็บ
        render_revenue_sources(
            df2,
            selected_month=selected_month,
            selected_province=selected_province,
            plotly_template=get_plotly_template(),
            key_prefix="tab1",
        )

        render_cdd_sources_embeds(key_prefix="tab1")

    with tab2:
        # กราฟ/วิเคราะห์อื่น ๆ สามารถเพิ่มต่อได้
        render_revenue_sources(
            df2,
            selected_month=selected_month,
            selected_province=selected_province,
            plotly_template=get_plotly_template(),
            key_prefix="tab2",
        )
        render_cdd_sources_embeds(key_prefix="tab2")

    # แหล่งข้อมูลด้านล่าง
    st.markdown("---")
    st.markdown(
        "แหล่งข้อมูลที่อ้างอิงในแดชบอร์ด:  "
        "[otop_r04](https://logi.cdd.go.th/otop/cdd_report/otop_r04.php) • "
        "[otop_r05](https://logi.cdd.go.th/otop/cdd_report/otop_r05.php) • "
        "[otop_r06](https://logi.cdd.go.th/otop/cdd_report/otop_r06.php)"
    )


if __name__ == "__main__":
    try:
        main()
    except Exception:
        st.set_page_config(page_title="OTOP Sales Dashboard", page_icon="🛍️", layout="wide")
        st.error("เกิดข้อผิดพลาดในแอป (รายละเอียดด้านล่าง)")
        st.code(traceback.format_exc())
