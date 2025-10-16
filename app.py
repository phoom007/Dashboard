# app.py
# -*- coding: utf-8 -*-
import streamlit as st

# ---------- Theme / Layout ----------
try:
    from utils.theme import set_base_page_config, inject_global_css, get_plotly_template
except Exception as e:
    # Fallback แบบเบา ๆ ถ้า utils.theme ยังไม่พร้อม
    def set_base_page_config():
        st.set_page_config(page_title="OTOP Dashboard", page_icon="🛍️", layout="wide")

    def inject_global_css():
        pass

    def get_plotly_template() -> str:
        return "plotly_white"

    st.sidebar.warning("⚠️ โหลด utils.theme ไม่ได้ — ใช้ค่าเริ่มต้นชั่วคราว")

# ---------- Data loaders ----------
try:
    from utils.data import load_all_data, load_geojson
except Exception as e:
    st.error("❌ ไม่สามารถนำเข้า utils.data ได้")
    st.exception(e)
    st.stop()

# ---------- Components (มี fallback หากหาไฟล์ไม่เจอ) ----------
_kpi_ok = _charts_ok = _map_ok = True
try:
    from components.kpi_card import render_kpis
except Exception:
    _kpi_ok = False

try:
    from components.charts import render_main_row_charts, render_transactions_and_sources
except Exception:
    _charts_ok = False

try:
    from components.mapbox import render_thailand_map
except Exception:
    _map_ok = False


def main() -> None:
    # 1) Page config & CSS
    set_base_page_config()
    inject_global_css()
    plotly_template = get_plotly_template()  # ใช้ "plotly_white" ตลอด

    # 2) Session defaults
    if "display_mode" not in st.session_state:
        st.session_state.display_mode = "Day"  # เริ่ม Day เสมอ

    # 3) โหลดข้อมูลแบบกันพัง
    try:
        loaded = load_all_data()
        if not isinstance(loaded, (list, tuple)) or len(loaded) != 6:
            raise ValueError(
                f"load_all_data() ต้องคืน 6 ค่า แต่ได้ชนิด {type(loaded)} "
                f"และจำนวน {len(loaded) if hasattr(loaded,'__len__') else 'unknown'}"
            )
        df1, df2, df3, df1_melted, national_avg, month_cols = loaded
    except Exception as e:
        st.error("❌ โหลดข้อมูลไม่สำเร็จจาก load_all_data()")
        st.caption("ตรวจไฟล์ utils/data.py ว่าคืนค่าครบ 6 ค่า และคอลัมน์ 'จังหวัด'/'เดือน' ตรงตามที่ใช้")
        st.exception(e)
        return  # กลับออกจาก main เพื่อไม่ให้หน้าโล่ง

    try:
        th_geo = load_geojson()  # อาจเป็น None ได้
    except Exception as e:
        th_geo = None
        st.warning("⚠️ โหลด GeoJSON ไม่สำเร็จ — แผนที่จะถูกปิดไว้")
        st.exception(e)

    # 4) Sidebar
    with st.sidebar:
        st.header("🎛️ การแสดงผลและตัวกรอง")
        is_night = st.toggle("Night 🌙", value=(st.session_state.display_mode == "Night"))
        st.session_state.display_mode = "Night" if is_night else "Day"

        selected_month = st.selectbox("เลือกเดือน", options=month_cols, index=len(month_cols) - 1)
        selected_province = st.selectbox("เลือกจังหวัด (สำหรับกราฟแนวโน้ม)", options=["ภาพรวม"] + df1.index.tolist(), index=0)

        channel_filter = st.multiselect("กรองตามช่องทาง (ถ้าว่าง = ทั้งหมด)", options=list(df2.columns), default=[])
        product_filter = st.multiselect("กรองตามประเภทสินค้า (ถ้าว่าง = ทั้งหมด)", options=list(df3.columns), default=[])

    # 5) Header
    st.title("🛍️ Dashboard สรุปผลการจำหน่ายสินค้า OTOP (ชุดเติบโต)")
    st.caption(
        f"ข้อมูลประจำเดือน **{selected_month}** • หน่วยเป็นบาท (฿) • "
        "แหล่งข้อมูล: **otop_r04, otop_r05, otop_r06** (ดูท้ายหน้า)"
    )

    # 6) KPI row
    if _kpi_ok:
        try:
            render_kpis(df1, df2, df3, selected_month)
        except Exception as e:
            st.error("เกิดข้อผิดพลาดขณะเรนเดอร์ KPI")
            st.exception(e)
    else:
        # Fallback: โชว์ตัวเลขหลัก ๆ ให้หน้าไม่โล่ง
        st.info("ℹ️ ใช้ KPI แบบย่อ (เพราะไม่พบ components.kpi_card)")
        total_sales = df1[selected_month].sum()
        top_province = df1[selected_month].idxmax()
        top_sales = df1[selected_month].max()
        st.metric("ยอดขายรวมทั้งประเทศ (เดือนที่เลือก)", f"฿{total_sales:,.0f}")
        st.metric("จังหวัดขายสูงสุด", top_province)
        st.metric("ยอดขายจังหวัดสูงสุด", f"฿{top_sales:,.0f}")

    # 7) Main charts row
    df2_view = df2 if not channel_filter else df2.loc[:, channel_filter]
    if _charts_ok:
        try:
            render_main_row_charts(
                df1=df1,
                df2=df2_view,
                selected_month=selected_month,
                plotly_template=plotly_template,
            )
        except Exception as e:
            st.error("เกิดข้อผิดพลาดขณะเรนเดอร์กราฟหลัก")
            st.exception(e)
    else:
        st.warning("⚠️ ไม่พบ components.charts — ข้ามกราฟหลักชั่วคราว")

    st.divider()

    # 8) Thailand map
    if _map_ok and th_geo is not None:
        try:
            st.subheader("แผนที่ประเทศไทย — ยอดขายรายจังหวัด")
            render_thailand_map(
                df1=df1,
                df1_melted=df1_melted,
                thailand_geojson=th_geo,
                selected_month=selected_month,
                theme_mode=st.session_state.display_mode,
            )
        except Exception as e:
            st.error("เกิดข้อผิดพลาดขณะเรนเดอร์แผนที่")
            st.exception(e)
    else:
        st.info("ℹ️ ปิดแผนที่ไว้ (ไม่พบโมดูล map หรือ geojson ไม่พร้อม)")

    st.divider()

    # 9) Transactions + Sources + Trend/Donut
    df3_view = df3 if not product_filter else df3.loc[:, product_filter]
    if _charts_ok:
        try:
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
        except Exception as e:
            st.error("เกิดข้อผิดพลาดขณะเรนเดอร์ส่วน Transactions/แหล่งข้อมูล/แนวโน้ม")
            st.exception(e)
    else:
        st.info("ℹ️ ข้ามส่วน Transactions/แหล่งข้อมูล/แนวโน้ม — ต้องใช้ components.charts")

    # 10) หมายเหตุท้ายหน้า
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


# ---------- Run (เรียกตรง ๆ เพื่อกันหน้าโล่ง) ----------
try:
    main()
except Exception as e:
    st.error("❌ แอปล้มในระดับ global main()")
    st.exception(e)
