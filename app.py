# app.py
# -*- coding: utf-8 -*-
import streamlit as st
import traceback

def main():
    from utils.theme import set_base_page_config, inject_global_css, get_plotly_template
    from utils.data import load_all_data, load_geojson
    from components.header import render_header          # header ว่าง
    from components.sidebar import render_sidebar
    from components.kpi_card import render_kpis
    from components.charts import render_main_row_charts, render_transactions_and_sources
    from components.mapbox import render_thailand_map

    # 0) Page setup
    set_base_page_config()
    inject_global_css()

    # 1) (header ว่าง)
    render_header()

    # 2) Data
    df1, df2, df3, df1_melted, national_avg, month_cols = load_all_data()
    th_geo = load_geojson()

    # 3) Sidebar filters
    sidebar_state = render_sidebar(df1, df2, df3)
    selected_month   = sidebar_state["selected_month"]
    selected_province = sidebar_state["selected_province"]
    channel_filter   = sidebar_state["channel_filter"]
    product_filter   = sidebar_state["product_filter"]

    # 4) Title -> Divider -> Caption (ตามที่ขอ)
    st.title("🛍️ Dashboard สรุปผลการจำหน่ายสินค้า OTOP (ชุดเติบโต)")
    st.divider()
    st.caption(
        f"ข้อมูลประจำเดือน **{selected_month}** • หน่วยเป็นบาท (฿) • แหล่งข้อมูล: "
        "otop_r04, otop_r05, otop_r06 (ดูท้ายหน้า)"
    )

    # 5) KPI
    render_kpis(df1, df2, df3, selected_month)
    st.markdown("")

    # 6) Main charts
    render_main_row_charts(df1, df2, selected_month, plotly_template=get_plotly_template())

    st.markdown("---")

    # 7) Tabs
    tab1, tab2 = st.tabs(["🗺️ ภาพรวมรายจังหวัด", "🔎 วิเคราะห์เชิงลึก"])
    with tab1:
        render_thailand_map(df1, df1_melted, th_geo, selected_month)
    with tab2:
        render_transactions_and_sources(
            df1, df2, df3, selected_month, selected_province,
            channel_filter, product_filter, national_avg,
            plotly_template=get_plotly_template()
        )

    # 8) Data sources
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
