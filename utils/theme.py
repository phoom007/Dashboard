import streamlit as st

PRIMARY_LIGHT = "#623F2A"   # น้ำตาลทองแนว OTOP
PRIMARY_DARK  = "#D7B889"

def set_base_page_config():
    st.set_page_config(page_title="OTOP Sales Dashboard", page_icon="🛍️", layout="wide")

def inject_global_css(mode="Light"):
    # ฟอนต์ Prompt สำหรับไทย + Inter สำหรับอังกฤษ
    base_css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;600;700&family=Inter:wght@400;600;700&display=swap');
    html, body, [class*="css"] {{
        font-family: 'Prompt', 'Inter', sans-serif;
    }}
    .kpi-card {{
        background-color: {"#FFFFFF" if mode=="Light" else "#1E1E1E"};
        padding: 1.2rem;
        border-radius: 16px;
        box-shadow: 0 6px 18px rgba(0,0,0,{0.08 if mode=="Light" else 0.35});
        border: 1px solid {"#E8E8E8" if mode=="Light" else "#333"};
        transition: all .25s ease;
    }}
    .kpi-card:hover {{
        transform: translateY(-3px);
        box-shadow: 0 10px 24px rgba(0,0,0,{0.12 if mode=="Light" else 0.5});
    }}
    .kpi-title {{ font-size: 0.95rem; font-weight: 600; color: {"#555" if mode=="Light" else "#BDBDBD"}; }}
    .kpi-value {{ font-size: 2rem; font-weight: 700; color: {"#1A237E" if mode=="Light" else "#90CAF9"}; }}
    .kpi-delta {{ font-size: 0.9rem; color: {"#888" if mode=="Light" else "#9E9E9E"}; }}
    .content-box {{
        background-color: {"#F8F9FA" if mode=="Light" else "#2C2C2C"};
        padding: 1rem; border-radius: 16px; border: 1px solid {"#E0E0E0" if mode=="Light" else "#424242"};
    }}
    </style>
    """
        # utils/theme.py (ตัวอย่างใส่เพิ่มในฟังก์ชัน inject_global_css)
    st.markdown("""
    <style>
    /* ปรับมุมโค้ง+เงานุ่มทั่วไป */
    .block-container { padding-top: 0.8rem; }
    div[data-testid="stHorizontalBlock"] > div { border-radius: 18px; }
    .stButton>button, .stDownloadButton>button, .stRadio, .stSelectbox {
        border-radius: 14px !important;
    }
    /* จัดระยะหัวข้อบน */
    h1,h2,h3 { margin-top: 0.4rem; }
    
    /* ปรับ label ของ toggle/checkbox ให้ชิดซ้ายดูสะอาด */
    label { font-weight: 500; }
    </style>
    """, unsafe_allow_html=True)

def get_plotly_template():
    return "plotly_white" if st.session_state.theme_mode=="Light" else "plotly_dark"

