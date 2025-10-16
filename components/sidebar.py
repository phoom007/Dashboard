# components/sidebar.py (แทนฟังก์ชัน render_sidebar ทั้งตัว)
import streamlit as st

def render_sidebar(df1, df2, df3):
    with st.sidebar:
        st.header("🧪 การแสดงผลและตัวกรอง")

        # ---- Day/Night Toggle (แถวบนสุด) ----
        if "display_mode" not in st.session_state:
            st.session_state.display_mode = "Day"  # เริ่ม Day เสมอ
        is_night = st.toggle("Night 🌙", value=(st.session_state.display_mode == "Night"))
        st.session_state.display_mode = "Night" if is_night else "Day"
        st.caption("Day ☀️ / Night 🌙 (พื้นหลังขาวเสมอ)")

        # ---- ตัวกรอง ----
        month_cols = list(df1.columns)
        selected_month = st.selectbox("เลือกเดือน", options=month_cols, index=len(month_cols)-1)

        selected_province = st.selectbox("เลือกจังหวัด (สำหรับกราฟแนวโน้ม)", options=['ภาพรวม'] + df1.index.tolist())

        channel_filter = st.multiselect("กรองตามช่องทาง (ถ้าไม่ว่าง = ทั้งหมด)", options=list(df2.columns))
        product_filter = st.multiselect("กรองตามประเภทสินค้า (ถ้าไม่ว่าง = ทั้งหมด)", options=list(df3.columns))

        st.divider()
        st.caption("เมนูเกี่ยวข้องเท่านั้น (ปุ่มใช้งานได้จริง):")
        st.checkbox("Dashboard", value=True, disabled=True)
        st.checkbox("Analytics", value=True, disabled=True)
        st.checkbox("Data: Provinces", value=True, disabled=True)
        st.checkbox("Data: Channels", value=True, disabled=True)
        st.checkbox("Data: Product Types", value=True, disabled=True)

    return {
        "selected_month": selected_month,
        "selected_province": selected_province,
        "channel_filter": channel_filter,
        "product_filter": product_filter,
    }
