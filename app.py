# app.py
# -*- coding: utf-8 -*-
import streamlit as st

# --- Theme / Layout ---
from utils.theme import (
    set_base_page_config,
    inject_global_css,
    get_plotly_template,
)

# --- Data loaders ---
from utils.data import (
    load_all_data,   # -> df1, df2, df3, df1_melted, national_average, month_cols
    load_geojson,    # -> thailand_geojson
)

# --- Components ---
from components.kpi_card import render_kpis
from components.charts import (
    render_main_row_charts,
    render_transactions_and_sources,
)
from components.mapbox import render_thailand_map


# =============================================================================
# App
# =============================================================================
def main() -> None:
    # 1) Page & CSS
    set_base_page_config()
    inject_global_css()
    plotly_template = get_plotly_template()  # "plotly_white"

    # 2) Session defaults (Night/Day toggle)
    if "display_mode" not in st.session_state:
        st.session_state.display_mode = "Day"   # เริ่ม Day เสมอ

    # 3) Load all data (cached inside utils.data)
    df1, df2, df3, df1_melted, national_avg, month_cols = load_all_data()
    th_geo = load_geojson()

    # 4) Sidebar controls
    with st.sidebar:
        st.header("🎛️ การแสดงผลและตัวกรอง")

        # Night/Day toggle (กระทบเฉพาะ KPI ผ่าน CSS)
        is_night = st.toggle("Night 🌙", value=(st.session_state.display_mode == "Night"))
        st.session_state.display_mode = "Night" if is_night else "Day"

        selected_month = st.selectbox(
            "เลือกเดือน",
            options=month_cols,
            index=len(month_cols) - 1,
        )

        selected_province = st.selectbox(
            "เลือกจังหวัด (สำหรับกราฟแนวโน้ม)",
            options=["ภาพรวม"] + df1.index.tolist(),
            index=0,
        )

        channel_filter = st.multiselect(
            "กรองตามช่องทาง (ถ้าว่าง = ทั้งหมด)",
            options=list(df2.columns),
            default=[],
        )

        product_filter = st.multiselect(
            "กรองตามประเภทสินค้า (ถ้าว่าง = ทั้งหมด)",
            options=list(df3.columns),
            default=[],
        )

    # 5) Header & subtitle
    st.title("🛍️ Dashboard สรุปผลการจำหน่ายสินค้า OTOP (ชุดเติบโต)")
    st.caption(
        f"ข้อมูลประจำเดือน **{selected_month}** • หน่วยเป็นบาท (฿) • "
        "แหล่งข้อมูล: **otop_r04, otop_r05, otop_r06** (ดูท้ายหน้า)"
    )

    # 6) KPI – 4 กล่องแถวเดียว
    render_kpis(df1, df2, df3, selected_month)

    # 7) Main row charts (ซ้าย: แนวโน้มรวม, ขวา: โครงสร้างช่องทาง)
    render_main_row_charts(
        df1=df1,
        df2=df2 if not channel_filter else df2.loc[:, channel_filter],
        selected_month=selected_month,
        plotly_template=plotly_template,
    )

    st.divider()

    # 8) แผนที่ประเทศไทย (สว่างตลอด)
    st.subheader("แผนที่ประเทศไทย — ยอดขายรายจังหวัด")
    render_thailand_map(
        df1=df1,
        df1_melted=df1_melted,
        thailand_geojson=th_geo,
        selected_month=selected_month,
        theme_mode=st.session_state.display_mode,  # ส่งต่อไว้เผื่อ component ใช้
    )

    st.divider()

    # 9) ส่วนลึก: แนวโน้มจังหวัด + แหล่งข้อมูล CDD + โดนัท Revenue Sources
    render_transactions_and_sources(
        df1=df1,
        df2=df2 if not channel_filter else df2.loc[:, channel_filter],
        df3=df3 if not product_filter else df3.loc[:, product_filter],
        selected_month=selected_month,
        selected_province=selected_province,
        channel_filter=channel_filter,
        product_filter=product_filter,
        national_avg=national_avg,
        plotly_template=plotly_template,
    )

    st.write("")  # spacer


# =============================================================================
# Entrypoint
# =============================================================================
if __name__ == "__main__":
    main()
