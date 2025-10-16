# app.py
# -*- coding: utf-8 -*-
import streamlit as st
import traceback

# ---- Local modules ----
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
    # 0) Base theme & CSS
    set_base_page_config()
    inject_global_css()

    # 1) Load data
    #    (utils/data.py ต้องคืน 6 ค่า: df1, df2, df3, df1_melted, national_avg, month_cols)
    df1, df2, df3, df1_melted, national_avg, month_cols = load_all_data()
    th_geo = load_geojson()

    # 2) Sidebar (โลโก้ซ้าย / Night Mode ขวา + ตัวกรอง)
    sidebar_state = render_sidebar(df1, df2, df3)
    selected_month = sidebar_state["selected_month"]
    selected_province = sidebar_state["selected_province"]
    channel_filter = sidebar_state["channel_filter"]
    product_filter = sidebar_state["product_filter"]

    # 3) Title + Caption (ตามสเปก)
    st.title("🛍️ Dashboard สรุปผลการจำหน่ายสินค้า OTOP (ชุดเติบโต)")
    st.divider()
    st.caption(
        f"ข้อมูลประจำเดือน **{selected_month}** • หน่วยเป็นบาท (฿) • "
        "แหล่งข้อมูล: otop_r04, otop_r05, otop_r06 (ดูท้ายหน้า)"
    )

    # 4) KPI (สีเดิม/ไอคอนเดิม/1 แถวบน Desktop, มือถือ 2x2)
    render_kpis(df1, df2, df3, selected_month)

    # 5) Global controls (เลื่อน) + Main charts (ซ้าย-ขวา)
    render_time_kind_controls(prefix="main")
    render_main_row_charts(
        df1, df2, selected_month,
        plotly_template=get_plotly_template(),
        key_prefix="main",
    )

    st.markdown("---")

    # 6) Tabs — ทั้งสองแท็บมี Controls + Revenue Sources + CDD Embeds
    tab1, tab2 = st.tabs(["🗺️ ภาพรวมรายจังหวัด", "🔎 วิเคราะห์เชิงลึก"])

    with tab1:
        # Controls (มี auto-unique key แล้ว, prefix เฉพาะแท็บ)
        render_time_kind_controls(prefix="tab1")

        # Thailand Map (Mapbox สว่างตลอด)
        render_thailand_map(
            df1=df1,
            df1_melted=df1_melted,
            th_geojson=th_geo,
            selected_month=selected_month,
            key_prefix="tab1",
        )

        st.markdown("---")

        # Revenue Sources (เดือนเดียว)
        render_revenue_sources(
            df2=df2,
            selected_month=selected_month,
            plotly_template=get_plotly_template(),
            key_prefix="tab1",
        )

        st.markdown("---")

        # CDD embeds (เลือกหน้า otop_r06/05/04)
        render_cdd_sources_embeds(key_prefix="tab1")

    with tab2:
        render_time_kind_controls(prefix="tab2")

        # (เว้นพื้นที่เพิ่มแผนวิเคราะห์เชิงลึกอื่น ๆ หากต้องการ)
        # แสดง Revenue Sources + CDD เช่นกัน
        st.markdown("---")
        render_revenue_sources(
            df2=df2,
            selected_month=selected_month,
            plotly_template=get_plotly_template(),
            key_prefix="tab2",
        )

        st.markdown("---")
        render_cdd_sources_embeds(key_prefix="tab2")

    # 7) Footer: Data sources
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
        # Fallback page config (กรณี error ก่อน set_page_config)
        try:
            st.set_page_config(page_title="OTOP Sales Dashboard", page_icon="🛍️", layout="wide")
        except Exception:
            pass
        st.error("เกิดข้อผิดพลาดในแอป (รายละเอียดอยู่ด้านล่าง)")
        st.code(traceback.format_exc())
