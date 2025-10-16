# app.py
# -*- coding: utf-8 -*-
import streamlit as st
import traceback

from utils.theme import set_base_page_config, inject_global_css, get_plotly_template
from utils.data import load_all_data, load_geojson
from components.sidebar import render_sidebar
from components.kpi_card import render_kpis
from components.charts import (
    render_time_kind_controls,
    render_main_row_charts,
    render_revenue_sources,
    render_cdd_sources_embeds,
)
from components.mapbox import render_thailand_map


def main():
    # 0) Base
    set_base_page_config()
    inject_global_css()

    # 1) Data
    df1, df2, df3, df1_melted, national_avg, month_cols = load_all_data()
    th_geo = load_geojson()

    # 2) Sidebar (โลโก้ซ้าย / Night Mode ขวา)
    s = render_sidebar(df1, df2, df3)
    selected_month     = s["selected_month"]
    selected_province  = s["selected_province"]
    channel_filter     = s["channel_filter"]
    product_filter     = s["product_filter"]

    # 3) Title + Caption (ตามที่กำหนด)
    st.title("🛍️ Dashboard สรุปผลการจำหน่ายสินค้า OTOP (ชุดเติบโต)")
    st.divider()
    st.caption(
        f"ข้อมูลประจำเดือน **{selected_month}** • หน่วยเป็นบาท (฿) • แหล่งข้อมูล: "
        "otop_r04, otop_r05, otop_r06 (ดูท้ายหน้า)"
    )

    # 4) KPI (สีเดิม/ไอคอนเดิม/เลย์เอาต์เดิม)
    render_kpis(df1, df2, df3, selected_month)

    # 5) Controls (เลื่อน) + กราฟหลัก (ซ้าย–ขวา)
    render_time_kind_controls(prefix="main")
    render_main_row_charts(df1, df2, selected_month, plotly_template=get_plotly_template())

    st.markdown("---")

    # 6) Tabs (ทั้งสองแท็บมี Controls + Revenue Sources + CDD)
    tab1, tab2 = st.tabs(["🗺️ ภาพรวมรายจังหวัด", "🔎 วิเคราะห์เชิงลึก"])

    with tab1:
        render_time_kind_controls(prefix="tab1")
        render_thailand_map(df1, df1_melted, th_geo, selected_month)
        st.markdown("---")
        render_revenue_sources(df2, selected_month, plotly_template=get_plotly_template())
        st.markdown("---")
        render_cdd_sources_embeds()

    with tab2:
        render_time_kind_controls(prefix="tab2")
        # (พื้นที่สำหรับกราฟวิเคราะห์เชิงลึกอื่น ๆ ของคุณ ถ้าต้องการเพิ่มในอนาคต)
        st.markdown("---")
        render_revenue_sources(df2, selected_month, plotly_template=get_plotly_template())
        st.markdown("---")
        render_cdd_sources_embeds()

    # 7) Footer sources
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
