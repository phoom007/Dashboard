# app.py
# -*- coding: utf-8 -*-
import streamlit as st
import traceback

# ============== Local modules ==============
from utils.theme import set_base_page_config, inject_global_css, get_plotly_template
from utils.data import load_all_data, load_geojson
from components.sidebar import render_sidebar
from components.kpi_card import render_kpis
from components.mapbox import render_thailand_map
from components.charts import (
    render_time_kind_controls,
    render_main_row_charts,
    render_revenue_sources,
    render_cdd_sources_embeds,
    render_regional_growth,
    render_product_category_performance,
)

# ============== App ==============
def main():
    # 0) Base config & CSS
    set_base_page_config()
    inject_global_css()  # พื้นหลังขาว, KPI 4 กล่องแถวเดียว, Night Mode เฉพาะ KPI

    # 1) Load data (ต้องได้ 6 ค่า)
    _loaded = load_all_data()
    if not isinstance(_loaded, tuple) or len(_loaded) != 6:
        raise ValueError("load_all_data() ต้องคืน 6 ค่า: (df1, df2, df3, df1_melted, national_avg, month_cols)")
    df1, df2, df3, df1_melted, national_avg, month_cols = _loaded

    th_geo = load_geojson()

    # 2) Sidebar (โลโก้ซ้าย / Night Mode ขวา + ตัวกรองที่เกี่ยวข้องเท่านั้น)
    sidebar_state = render_sidebar(df1, df2, df3)
    selected_month     = sidebar_state["selected_month"]
    selected_province  = sidebar_state["selected_province"]
    channel_filter     = sidebar_state["channel_filter"]
    product_filter     = sidebar_state["product_filter"]

    # 3) Title + Caption (ตามสเปกข้อความบนสุด)
    st.title("🛍️ Dashboard สรุปผลการจำหน่ายสินค้า OTOP (ชุดเติบโต)")
    st.divider()
    st.caption(
        f"ข้อมูลประจำเดือน **{selected_month}** • หน่วยเป็นบาท (฿) • "
        "แหล่งข้อมูล: otop_r04, otop_r05, otop_r06 (ดูท้ายหน้า)"
    )

    # 4) KPI (สีเดิม/ไอคอนเดิม/เดสก์ท็อป 4 กล่องแถวเดียว, มือถือเลื่อนได้)
    render_kpis(df1, df2, df3, selected_month)

    # 5) Global controls + Main charts (ซ้าย-ขวา)
    render_time_kind_controls(prefix="main")
    render_main_row_charts(
        df1=df1,
        df2=df2,
        selected_month=selected_month,
        month_cols=month_cols,                 # ✅ ส่ง month_cols
        selected_province=selected_province,   # ✅ ส่งจังหวัดที่เลือก
        plotly_template=get_plotly_template(),
        key_prefix="main",
    )
    
    st.markdown("---")
    
    # 6) กราฟใหม่ 2 อัน (ให้ตอบสนองจังหวัดด้วย)
    render_regional_growth(
        df1=df1,
        month_cols=month_cols,
        selected_month=selected_month,
        selected_province=selected_province,   # ✅ ไฮไลต์ภูมิภาคของจังหวัดที่เลือก
        plotly_template=get_plotly_template(),
        key_prefix="below_main",
    )
    
    render_product_category_performance(
        df3=df3,
        selected_month=selected_month,
        selected_province=selected_province,   # ✅ แสดงป้ายแจ้ง และหัวข้อสะท้อนจังหวัดที่เลือก
        plotly_template=get_plotly_template(),
        key_prefix="below_main",
    )
    st.markdown("---")

    # 7) Tabs — ทั้งสองแท็บมี Revenue Sources (เดือนเดียว) และ CDD Embeds
    tab1, tab2 = st.tabs(["🗺️ ภาพรวมรายจังหวัด", "🔎 วิเคราะห์เชิงลึก"])

    with tab1:
        # Controls เฉพาะในแท็บ (กันชน key อัตโนมัติ)
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

        # CDD embeds (เลือกหน้า otop_r06/05/04) — iframe ไม่ใส่ key
        render_cdd_sources_embeds(key_prefix="tab1")

    with tab2:
        # Controls เฉพาะในแท็บ (กันชน key อัตโนมัติ)
        render_time_kind_controls(prefix="tab2")

        # (พื้นที่สำหรับกราฟเจาะลึกอื่น ๆ เพิ่มได้ภายหลัง)
        st.markdown("---")

        # Revenue Sources (เดือนเดียว) — แสดงทั้งสองแท็บตามสเปก
        render_revenue_sources(
            df2=df2,
            selected_month=selected_month,
            plotly_template=get_plotly_template(),
            key_prefix="tab2",
        )

        st.markdown("---")

        # CDD embeds — แสดงทั้งสองแท็บตามสเปก
        render_cdd_sources_embeds(key_prefix="tab2")

    # 8) Footer: Data sources (ลิงก์อ้างอิงชัดเจน)
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
        # กันกรณี error ก่อน set_page_config
        try:
            st.set_page_config(page_title="OTOP Sales Dashboard", page_icon="🛍️", layout="wide")
        except Exception:
            pass
        st.error("เกิดข้อผิดพลาดในแอป (รายละเอียดอยู่ด้านล่าง)")
        st.code(traceback.format_exc())
