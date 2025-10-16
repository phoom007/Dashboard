# app.py (เฉพาะส่วนสำคัญที่ต้องแก้)
# -*- coding: utf-8 -*-
import streamlit as st
import traceback
from utils.theme import set_base_page_config, inject_global_css, get_plotly_template
from utils.data import load_all_data, load_geojson
from components.header import render_header
from components.sidebar import render_sidebar
from components.kpi_card import render_kpis
from components.charts import (
    render_main_row_charts,
    render_transactions_and_sources,
    render_revenue_sources,
    render_cdd_sources_embeds,
)
from components.mapbox import render_thailand_map

def main():
    set_base_page_config()
    inject_global_css()
    render_header()

    df1, df2, df3, df1_melted, national_avg, month_cols = load_all_data()
    th_geo = load_geojson()

    sidebar_state = render_sidebar(df1, df2, df3)
    selected_month = sidebar_state["selected_month"]
    selected_province = sidebar_state["selected_province"]
    channel_filter = sidebar_state["channel_filter"]
    product_filter = sidebar_state["product_filter"]

    st.title("🛍️ Dashboard สรุปผลการจำหน่ายสินค้า OTOP (ชุดเติบโต)")
    st.caption(
        f"ข้อมูลประจำเดือน **{selected_month}** • หน่วยเป็นบาท (฿) • แหล่งข้อมูล: "
        "otop_r04, otop_r05, otop_r06 (ดูท้ายหน้า)"
    )

    render_kpis(df1, df2, df3, selected_month)

    st.markdown("")  # เว้นบรรทัด
    render_main_row_charts(df1, df2, selected_month, plotly_template=get_plotly_template())
    st.markdown("---")

    tab1, tab2 = st.tabs(["🗺️ ภาพรวมรายจังหวัด", "🔎 วิเคราะห์เชิงลึก"])

    with tab1:
        render_thailand_map(df1, df1_melted, th_geo, selected_month)
        st.markdown("---")
        # >>> เพิ่มสองส่วนในแท็บนี้ <<<
        render_revenue_sources(df2, selected_month, plotly_template=get_plotly_template())
        st.markdown("---")
        render_cdd_sources_embeds()

    with tab2:
        render_transactions_and_sources(
            df1, df2, df3, selected_month, selected_province,
            channel_filter, product_filter, national_avg,
            plotly_template=get_plotly_template()
        )
        # (ฟังก์ชันนี้ตอนท้ายผมใส่สองส่วนไว้แล้ว
        #  แต่ถ้าคุณอยากเรียกซ้ำที่นี่อีกก็ได้ ไม่มีผลข้างเคียง)

if __name__ == "__main__":
    try:
        main()
    except Exception:
        st.set_page_config(page_title="OTOP Sales Dashboard", page_icon="🛍️", layout="wide")
        st.error("เกิดข้อผิดพลาดในแอป (รายละเอียดด้านล่าง)")
        st.code(traceback.format_exc())
