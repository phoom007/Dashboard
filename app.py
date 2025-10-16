from utils.theme import set_base_page_config, inject_global_css, get_plotly_template
import streamlit as st

set_base_page_config()
inject_global_css()
plotly_template = get_plotly_template()

# toggle (เริ่ม Day เสมอ)
if "display_mode" not in st.session_state:
    st.session_state.display_mode = "Day"
is_night = st.toggle("Night 🌙", value=(st.session_state.display_mode == "Night"))
st.session_state.display_mode = "Night" if is_night else "Day"
