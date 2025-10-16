# components/sidebar.py
# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd

LOGO_URL = "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/OTOP_Logo.svg/375px-OTOP_Logo.svg.png"

def _month_cols(df1: pd.DataFrame):
    cols = [c for c in df1.columns if ("2566" in c or "2567" in c)]
    return cols if cols else list(df1.columns)

def render_sidebar(df1: pd.DataFrame, df2: pd.DataFrame, df3: pd.DataFrame):
    with st.sidebar:
        c_logo, c_toggle = st.columns([1, 1])
        with c_logo:
            st.image(LOGO_URL, width=54)
        with c_toggle:
            if "display_mode" not in st.session_state:
                st.session_state.display_mode = "Day"
            night = st.toggle("Night Mode", value=(st.session_state.display_mode == "Night"), key="night_toggle")
            st.session_state.display_mode = "Night" if night else "Day"

        st.markdown("### การแสดงผลและตัวกรอง")

        months = _month_cols(df1)
        sel_month = st.selectbox("เลือกเดือน", options=months, index=len(months) - 1)

        sel_province = st.selectbox(
            "เลือกจังหวัด (สำหรับกราฟแนวโน้ม)",
            options=["ภาพรวม"] + df1.index.tolist(),
            index=0,
        )

        ch_cols = list(df2.columns)
        sel_channels = st.multiselect(
            "กรองตามช่องทาง (ถ้าไม่เลือก = ทั้งหมด)",
            options=ch_cols,
            default=ch_cols,
        )

        p_cols = list(df3.columns)
        sel_products = st.multiselect(
            "กรองตามประเภทสินค้า (ถ้าไม่เลือก = ทั้งหมด)",
            options=p_cols,
            default=p_cols,
        )

    return {
        "selected_month": sel_month,
        "selected_province": sel_province,
        "channel_filter": sel_channels,
        "product_filter": sel_products,
    }
