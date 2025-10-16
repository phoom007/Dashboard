import streamlit as st
import traceback

def main():
    from utils.theme import set_base_page_config, inject_global_css, get_plotly_template
    from utils.data import load_all_data, load_geojson
    from components.header import render_header            # <-- เพิ่มบรรทัดนี้
    from components.sidebar import render_sidebar
    from components.kpi_card import render_kpis
    from components.charts import render_main_row_charts, render_transactions_and_sources
    from components.mapbox import render_thailand_map

    set_base_page_config()
    inject_global_css()             # <-- ไม่มีพารามิเตอร์แล้ว
    render_header()
    
    template = get_plotly_template()

    # โหลดข้อมูล (ส่วนนี้ถ้าพัง เราจะจับด้านล่าง)
    df1, df2, df3, df1_melted, national_avg = load_all_data()
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
    st.markdown("")
    render_main_row_charts(df1, df2, selected_month, plotly_template=get_plotly_template())

    st.markdown("---")
    tab1, tab2 = st.tabs(["🗺️ ภาพรวมรายจังหวัด", "🔎 วิเคราะห์เชิงลึก"])
    with tab1:
        # ถ้าโหลดแผนที่ไม่ได้ ก็ข้ามอย่างสุภาพ
        if th_geo is None:
            st.info("ไม่สามารถแสดงแผนที่ได้ (ระบบยังทำงานส่วนอื่นตามปกติ)")
        else:
            render_thailand_map(df1, df1_melted, th_geo, selected_month, theme_mode=st.session_state.theme_mode)
    with tab2:
        render_transactions_and_sources(
            df1, df2, df3, selected_month, selected_province,
            channel_filter, product_filter, national_avg,
            plotly_template=get_plotly_template()
        )

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
