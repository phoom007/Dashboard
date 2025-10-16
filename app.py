# app.py
# -*- coding: utf-8 -*-
import streamlit as st
import traceback

# ---- Utils & Components ----
from utils.theme import set_base_page_config, inject_global_css, get_plotly_template
from utils.data import load_all_data, load_geojson

from components.sidebar import render_sidebar
from components.kpi_card import render_kpis
from components.mapbox import render_thailand_map

from components.charts import (
    render_time_kind_controls,
    render_main_row_charts,
    render_regional_growth,
    render_product_category_performance,
    render_revenue_sources,
    render_cdd_sources_embeds,
    # NEW 4 charts
    render_province_vs_avg_trend,
    render_mom_change_by_province,
    render_monthly_heatmap_selected,
    render_channel_cumulative_ytd,
)

# -------------------------------------------------
# Main
# -------------------------------------------------
def main() -> None:
    # 0) Base setup (พื้นหลังขาวตลอด)
    set_base_page_config()
    inject_global_css()  # CSS กลาง (KPI 4 กล่อง/บรรทัด, Night เฉพาะ KPI)

    # 1) Data
    df1, df2, df3, df1_melted, national_avg, month_cols = load_all_data()
    th_geo = load_geojson()

    # 2) Sidebar (โลโก้ + Night/Day toggle + ฟิลเตอร์)
    sidebar_state = render_sidebar(df1, df2, df3)
    selected_month     = sidebar_state.get("selected_month")
    selected_province  = sidebar_state.get("selected_province", "ภาพรวม")
    channel_filter     = sidebar_state.get("channel_filter", None)  # เผื่อมีใช้ภายหน้า
    product_filter     = sidebar_state.get("product_filter", None)  # เผื่อมีใช้ภายหน้า

    # 3) Title (ตามฟอร์แมตที่กำหนด)
    st.title("Dashboard สรุปผลการจำหน่ายสินค้า OTOP (ชุดเติบโต)")
    st.caption(
        f"ข้อมูลประจำเดือน **{selected_month}** • หน่วยเป็นบาท (฿) • แหล่งข้อมูล: otop_r04, otop_r05, otop_r06 (ดูท้ายหน้า)"
    )

    # 4) KPI (4 กล่องแนวนอน บนบรรทัดเดียว)
    render_kpis(df1, df2, df3, selected_month)
    st.markdown("")

    # 5) Global controls + Main charts (ซ้าย-ขวา)
    render_time_kind_controls(prefix="main")
    render_main_row_charts(
        df1=df1,
        df2=df2,
        selected_month=selected_month,
        month_cols=month_cols,
        selected_province=selected_province,
        plotly_template=get_plotly_template(),
        key_prefix="main",
    )

    st.markdown("---")

    # 6) Tabs
    tab1, tab2 = st.tabs(["🗺️ ภาพรวมรายจังหวัด", "🔎 วิเคราะห์เชิงลึก"])

    # 6.1 Tab 1 — แผนที่ + Revenue Sources + CDD
    with tab1:
        # แผนที่ประเทศไทย (Mapbox โทนสว่างเสมอ)
        render_thailand_map(
            df1=df1,
            df1_melted=df1_melted,
            thailand_geojson=th_geo,
            selected_month=selected_month
        )

        st.markdown("---")
        # Revenue Sources (เดือนเดียว)
        render_revenue_sources(
            df2=df2,
            selected_month=selected_month,
            plotly_template=get_plotly_template(),
            key_prefix="tab1"
        )

        st.markdown("---")
        # CDD embeds (เลือกหน้าได้ 3 เว็บ)
        render_cdd_sources_embeds(key_prefix="tab1")

    # 6.2 Tab 2 — วิเคราะห์เชิงลึก + Revenue Sources + CDD
    with tab2:
        # ตัวคุม (ช่วงเวลา/ชนิดกราฟ) สำหรับฝั่งวิเคราะห์
        render_time_kind_controls(prefix="deep")

        # Regional Growth (ไฮไลต์ region ของจังหวัดที่เลือก)
        render_regional_growth(
            df1=df1,
            month_cols=month_cols,
            selected_month=selected_month,
            selected_province=selected_province,
            plotly_template=get_plotly_template(),
            key_prefix="deep"
        )

        # Product Category (แสดงระดับประเทศ พร้อมแจ้งเตือนเมื่อเลือกจังหวัด)
        render_product_category_performance(
            df3=df3,
            selected_month=selected_month,
            selected_province=selected_province,
            plotly_template=get_plotly_template(),
            key_prefix="deep"
        )

        # ---- NEW: 4 charts (2 แถว x 2 คอลัมน์) ----
        st.markdown("---")
        st.subheader("มุมมองเพิ่มเติม (ปรับตามเดือน/จังหวัดที่เลือก)")
        c1, c2 = st.columns(2, gap="large")
        with c1:
            render_province_vs_avg_trend(
                df1=df1,
                month_cols=month_cols,
                selected_province=selected_province,
                plotly_template=get_plotly_template(),
                key_prefix="extra_row1_left",
            )
        with c2:
            render_mom_change_by_province(
                df1=df1,
                month_cols=month_cols,
                selected_month=selected_month,
                selected_province=selected_province,
                plotly_template=get_plotly_template(),
                key_prefix="extra_row1_right",
            )

        c3, c4 = st.columns(2, gap="large")
        with c3:
            render_monthly_heatmap_selected(
                df1=df1,
                month_cols=month_cols,
                selected_month=selected_month,
                selected_province=selected_province,
                plotly_template=get_plotly_template(),
                key_prefix="extra_row2_left",
            )
        with c4:
            render_channel_cumulative_ytd(
                df2=df2,
                month_cols=month_cols,
                selected_month=selected_month,
                plotly_template=get_plotly_template(),
                key_prefix="extra_row2_right",
            )

        st.markdown("---")
        # Revenue Sources & CDD (แสดงใน Tab นี้ด้วย ตามที่ขอ)
        render_revenue_sources(
            df2=df2,
            selected_month=selected_month,
            plotly_template=get_plotly_template(),
            key_prefix="tab2"
        )
        st.markdown("---")
        render_cdd_sources_embeds(key_prefix="tab2")

    # 7) Data sources (ท้ายหน้า)
    st.markdown("---")
    st.markdown(
        "แหล่งข้อมูลที่อ้างอิงในแดชบอร์ด:  "
        "[otop_r04](https://logi.cdd.go.th/otop/cdd_report/otop_r04.php) • "
        "[otop_r05](https://logi.cdd.go.th/otop/cdd_report/otop_r05.php) • "
        "[otop_r06](https://logi.cdd.go.th/otop/cdd_report/otop_r06.php)"
    )


# -------------------------------------------------
# Entrypoint (แสดง traceback เมื่อมี error)
# -------------------------------------------------
if __name__ == "__main__":
    try:
        main()
    except Exception:
        st.set_page_config(page_title="OTOP Sales Dashboard", page_icon="🛍️", layout="wide")
        st.error("เกิดข้อผิดพลาดในแอป (รายละเอียดด้านล่าง)")
        st.code(traceback.format_exc())
