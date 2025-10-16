# components/header.py
# -*- coding: utf-8 -*-
import streamlit as st

LOGO_URL = "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/OTOP_Logo.svg/375px-OTOP_Logo.svg.png"

def render_header():
    # init
    if "display_mode" not in st.session_state:
        st.session_state.display_mode = "Day"  # เริ่ม Day เสมอ

    left, spacer, right = st.columns([2, 6, 1])
    with left:
        st.markdown("<div style='font-weight:600;margin-bottom:6px;'>Mode</div>", unsafe_allow_html=True)
        is_night = st.toggle("Night 🌙", value=(st.session_state.display_mode == "Night"))
        st.session_state.display_mode = "Night" if is_night else "Day"
        st.caption("Day ☀️ / Night 🌙 (พื้นหลังขาวเสมอ)")

    with right:
        st.image(LOGO_URL, width=56)

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
