import streamlit as st
from utils.data import month_cols

def render_sidebar(df1, df2, df3):
    with st.sidebar:
        st.header("🎨 การแสดงผลและตัวกรอง")

        selected_month = st.selectbox(
            "เลือกเดือน", options=month_cols, index=len(month_cols)-1
        )

        selected_province = st.selectbox(
            "เลือกจังหวัด (สำหรับกราฟแนวโน้ม)", options=["ภาพรวม"] + df1.index.tolist()
        )

        channel_filter = st.multiselect(
            "กรองตามช่องทาง (ถ้าเว้นว่าง = ทั้งหมด)", 
            options=df2.columns.tolist(), default=[]
        )

        product_filter = st.multiselect(
            "กรองตามประเภทสินค้า (ถ้าเว้นว่าง = ทั้งหมด)",
            options=df3.columns.tolist(), default=[]
        )

        st.markdown("---")
        st.caption("เมนูเกี่ยวข้องเท่านั้น (ปุ่มใช้งานได้จริง):")
        page = st.radio("ไปยังส่วน:", ["Dashboard", "Analytics", "Data: Provinces", "Data: Channels", "Data: Product Types"],
                        label_visibility="collapsed", horizontal=False)
        st.session_state.current_page = page

    return {
        "selected_month": selected_month,
        "selected_province": selected_province,
        "channel_filter": channel_filter,
        "product_filter": product_filter,
    }
