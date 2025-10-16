# app.py
# -*- coding: utf-8 -*-
import streamlit as st

# ---------- Theme / Layout ----------
from utils.theme import (
    set_base_page_config,
    inject_global_css,
    get_plotly_template,
)

# ---------- Data loaders ----------
from utils.data import (
    load_all_data,   # -> df1, df2, df3, df1_melted, national_avg, month_cols
    load_geojson,    # -> thailand_geojson
)

# ---------- Components ----------
from components.kpi_card import render_kpis
from components.charts import (
    render_main_row_charts,
    render_transactions_and_sources,
)
from components.mapbox import render_thailand_map


def main() -> None:
    # 1) Page config & CSS (ต้องทำก่อนวาด UI)
    set_base_page_config()
    inject_global_css()
    plotly_template = get_plotly_template()  # "plotly_white"

    # 2) Session defaults
    if "display_mode" not in st.session_state:
        st.session_state.display_mode = "Day"  # เริ่ม Day เสมอ

    # 3) โหลดข้อมูล (กันพัง + debug panel)
    try:
        loaded = load_all_data()
        if not isinstance(loaded, (list, tuple)) or len(loaded) != 6:
            raise ValueError(
                f"load_all_data() ต้องคืน 6 ค่า แต่ได้ {type(loaded)} "
                f"ความยาว {len(loaded) if hasattr(loaded,'__len__') else 'unknown'}"
            )
        df1, df2, df3, df1_melted, national_avg, month_cols = loaded
    except Exception as e:
        st.error("❌ โหลดข้อมูลไม่สำเร็จจาก load_all_data()")
        st.caption("ตรวจไฟล์ utils/data.py ว่าคืนค่าครบ 6 ค่า และคอลัมน์ 'จังหวัด'/'เดือน' ตรงตามที่ใช้")
        st.exception(e)
        st.stop()

    th_geo = load_geojson()  # ไม่พังต่อให้ None — ตัวเรนเดอร์แผนที่จะ handle เอง

    # 4) Sidebar (โหมด/ฟิลเตอร์)
    with st.sidebar:
        st.header("🎛️ การแสดงผลและตัวกรอง")

        # Night/Day toggle (กระทบเฉพาะ KPI ผ่าน CSS; พื้นหลังทั้งแอปยังขาว)
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

    # 5) ส่วนหัว
    st.title("🛍️ Dashboard สรุปผลการจำหน่ายสินค้า OTOP (ชุดเติบโต)")
    st.caption(
        f"ข้อมูลประจำเดือน **{selected_month}** • หน่วยเป็นบาท (฿) • "
        "แหล่งข้อมูล: **otop_r04, otop_r05, otop_r06** (ดูท้ายหน้า)"
    )

    # 6) KPI – 4 กล่อง “แถวเดียว” (HTML เดียว)
    render_kpis(df1, df2, df3, selected_month)

    # 7) กราฟหลักแถวแรก (ซ้าย: แนวโน้มรวม, ขวา: โครงสร้างช่องทาง)
    df2_view = df2 if not channel_filter else df2.loc[:, channel_filter]
    render_main_row_charts(
        df1=df1,
        df2=df2_view,
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
        theme_mode=st.session_state.display_mode,
    )

    st.divider()

    # 9) แนวโน้มจังหวัด + แหล่งข้อมูล CDD (ฝัง r06/r05/r04) + โดนัท Revenue Sources
    df3_view = df3 if not product_filter else df3.loc[:, product_filter]
    render_transactions_and_sources(
        df1=df1,
        df2=df2_view,
        df3=df3_view,
        selected_month=selected_month,
        selected_province=selected_province,
        channel_filter=channel_filter,
        product_filter=product_filter,
        national_avg=national_avg,
        plotly_template=plotly_template,
    )

    # 10) เชิงอธิบายท้ายหน้า (อ้างอิงแหล่งข้อมูล)
    with st.expander("ℹ️ เกี่ยวกับข้อมูลและการคำนวณ (คลิกเพื่อดู)"):
        st.markdown(
            "- หน่วยเงิน: บาท (฿) ตลอดทั้งระบบ\n"
            "- คำนิยาม:\n"
            "  - **ยอดขายรวมทั้งประเทศ**: ผลรวมยอดขายทุกจังหวัดของเดือนที่เลือกจาก `df1`\n"
            "  - **จังหวัดขายสูงสุด**: จังหวัดที่มียอดขายสูงสุดในเดือนที่เลือกจาก `df1`\n"
            "  - **ประเภทขายดีที่สุด**: ประเภทสินค้าที่มียอดขายสูงสุดในเดือนที่เลือกจาก `df3`\n"
            "- แหล่งข้อมูลต้นทางที่อ้างอิงในแดชบอร์ด: r04 (รายจังหวัด), r05 (ประเภทสินค้า), r06 (ช่องทาง)\n"
            "  และถูกฝังให้ดูในแท็บภายในแดชบอร์ดแล้ว"
        )


# ------------------ Run (เรียกตรง ๆ กันหน้าโล่ง) ------------------
main()
