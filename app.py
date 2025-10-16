# -*- coding: utf-8 -*-
# OTOP Sales Dashboard — ชุด B (เน้นเทรนด์/เติบโต)
import streamlit as st
from utils.theme import set_base_page_config, inject_global_css, get_plotly_template
from utils.data import load_all_data, load_geojson, month_cols, PROVINCE_NAME_MAP
from components.topbar import render_topbar
from components.sidebar import render_sidebar
from components.kpi_card import render_kpis
from components.charts import render_main_row_charts, render_transactions_and_sources
from components.mapbox import render_thailand_map

# 0) Page setup
set_base_page_config()
if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "Light"

inject_global_css(st.session_state.theme_mode)

# 1) Topbar (สวย—ปุ่มส่วนใหญ่โชว์, Theme toggle ใช้งานจริง)
render_topbar()

# 2) Load data
df1, df2, df3, df1_melted, national_avg = load_all_data()
th_geo = load_geojson()

# 3) Sidebar (Filters & Nav)
sidebar_state = render_sidebar(df1, df2, df3)
selected_month = sidebar_state["selected_month"]
selected_province = sidebar_state["selected_province"]
channel_filter = sidebar_state["channel_filter"]
product_filter = sidebar_state["product_filter"]

# 4) Title + data source refs
st.title("🛍️ Dashboard สรุปผลการจำหน่ายสินค้า OTOP (ชุดเติบโต)")
st.caption(f"ข้อมูลประจำเดือน **{selected_month}** • หน่วยเป็นบาท (฿) • แหล่งข้อมูลอ้างอิง: "
           "otop_r04, otop_r05, otop_r06 จากระบบรายงาน CDD (ลิงก์ดูด้านล่างหน้า)")

# 5) KPI (ชุด B): (1) Total Sales, (2) Top Province, (3) Online Share %, (6) Total Sales MoM %, (7) Fastest Growing Province (MoM)
render_kpis(df1, df2, df3, selected_month)

st.markdown("")

# 6) กราฟหลักแถวแรก (ซ้าย: แนวโน้มรายได้, ขวา: โครงสร้างช่องทางแบบสลับประเภทแท่งได้)
render_main_row_charts(df1, df2, selected_month, plotly_template=get_plotly_template())

st.markdown("---")

# 7) แท็บแผนที่/วิเคราะห์
tab1, tab2 = st.tabs(["🗺️ ภาพรวมรายจังหวัด", "🔎 วิเคราะห์เชิงลึก"])
with tab1:
    render_thailand_map(df1, df1_melted, th_geo, selected_month, theme_mode=st.session_state.theme_mode)
with tab2:
    render_transactions_and_sources(df1, df2, df3, selected_month, selected_province,
                                    channel_filter, product_filter, national_avg,
                                    plotly_template=get_plotly_template())

# 8) แสดงเครดิตแหล่งข้อมูล (ตามสเปกข้อ 9)
st.markdown("---")
st.markdown(
    "แหล่งข้อมูลที่อ้างอิงในแดชบอร์ด:  "
    "[otop_r04](https://logi.cdd.go.th/otop/cdd_report/otop_r04.php) • "
    "[otop_r05](https://logi.cdd.go.th/otop/cdd_report/otop_r05.php) • "
    "[otop_r06](https://logi.cdd.go.th/otop/cdd_report/otop_r06.php)"
)
