# components/header.py
# -*- coding: utf-8 -*-
import streamlit as st

LOGO_URL = "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/OTOP_Logo.svg/375px-OTOP_Logo.svg.png"

def render_header():
    # แถวบน: ซ้ายเป็นโหมดเช้า/ค่ำ, ขวาเป็นโลโก้
    container = st.container()
    with container:
        left, spacer, right = st.columns([1.2, 6, 1])
        with left:
            st.markdown("<div style='font-weight:600;margin-bottom:6px;'>โหมด</div>", unsafe_allow_html=True)
            # ใช้ toggle ถ้ามี / ถ้าไม่มีใช้ checkbox
            default_dark = (st.session_state.get("theme_mode", "Light") == "Dark")
            if hasattr(st, "toggle"):
                is_dark = st.toggle("ค่ำ  🌙", value=default_dark)
            else:
                is_dark = st.checkbox("ค่ำ  🌙", value=default_dark)
            st.session_state.theme_mode = "Dark" if is_dark else "Light"
        with right:
            st.image(LOGO_URL, width=64)
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
