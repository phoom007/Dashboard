# components/topbar.py (แทนที่ฟังก์ชัน render_topbar ทั้งหมด)
import streamlit as st
from datetime import datetime

LOGO_URL = "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/OTOP_Logo.svg/375px-OTOP_Logo.svg.png"

def render_topbar():
    with st.container():
        colL, colM, colR = st.columns([1.2, 5, 2])
        with colL:
            st.image(LOGO_URL, width=54)
        with colM:
            st.text_input("🔎 ค้นหา (ตกแต่งเพื่อความสวยงาม)", value="", placeholder="พิมพ์เพื่อค้นหา…", label_visibility="collapsed")
        with colR:
            c1, c2, c3, c4 = st.columns([1,1,1,2])
            with c1:
                st.write("🕒")
                st.caption(datetime.now().strftime("%H:%M"))
            with c2:
                st.write("🔔")
                st.caption("แจ้งเตือน")
            with c3:
                st.write("⚙️")
                st.caption("ตั้งค่า")
            with c4:
                # Theme toggle (fallback ถ้าไม่มี st.toggle)
                if hasattr(st, "toggle"):
                    mode_on = st.toggle("Dark", value=(st.session_state.theme_mode=="Dark"), label_visibility="collapsed")
                else:
                    mode_on = st.checkbox("Dark", value=(st.session_state.theme_mode=="Dark"))
                st.session_state.theme_mode = "Dark" if mode_on else "Light"
                st.write("👤")
                st.caption("โปรไฟล์")
    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
