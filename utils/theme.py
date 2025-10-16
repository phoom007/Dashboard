# utils/theme.py (เฉพาะส่วนฟังก์ชัน — ถ้ามีอยู่แล้ว ให้เติม KPI CSS ด้านล่าง)
import streamlit as st

def set_base_page_config():
    st.set_page_config(page_title="OTOP Sales Dashboard", page_icon="🛍️", layout="wide")

def get_plotly_template():
    return "plotly_dark" if st.session_state.get("theme_mode","Light")=="Dark" else "plotly_white"

def inject_global_css(theme_mode: str = "Light"):
    is_dark = (theme_mode == "Dark")
    bg     = "#101214" if is_dark else "#ffffff"
    text   = "#E6E8EA" if is_dark else "#1F2A37"
    mute   = "#9AA4B2" if is_dark else "#6B7280"
    kpi_bg = "#161A1E" if is_dark else "#0f172a"
    kpi_fg = "#DDE3EA" if is_dark else "#E2E8F0"
    kpi_shadow = "0 10px 30px rgba(0,0,0,.45)" if is_dark else "0 10px 24px rgba(2,6,23,.18)"

    st.markdown(f"""
    <style>
      html, body, [data-testid="stAppViewContainer"] {{
        background: {bg};
        color: {text};
      }}
      /* ===== KPI CSS ===== */
      .kpi-grid {{
        display: grid;
        grid-template-columns: repeat(4, minmax(0,1fr));
        gap: 18px;
        margin: 10px 0 18px 0;
      }}
      @media (max-width: 1400px) {{
        .kpi-grid {{ grid-template-columns: repeat(2, minmax(0,1fr)); }}
      }}
      @media (max-width: 700px) {{
        .kpi-grid {{ grid-template-columns: 1fr; }}
      }}
      .kpi-card {{
        position: relative;
        border-radius: 18px;
        background: linear-gradient(180deg, {kpi_bg}, rgba(15,23,42,.85));
        border: 1px solid rgba(148,163,184,.12);
        box-shadow: {kpi_shadow};
        padding: 18px 18px 16px 18px;
        transition: transform .15s ease, box-shadow .2s ease, border-color .2s ease;
      }}
      .kpi-card:hover {{ transform: translateY(-2px); border-color: rgba(148,163,184,.28); }}
      .kpi-ic {{
        font-size: 22px; line-height: 22px; margin-right: 10px;
      }}
      .kpi-title {{
        font-weight: 600; font-size: 14px; color: {mute}; letter-spacing: .2px;
        display:flex; align-items:center;
      }}
      .kpi-value {{
        font-size: 28px; font-weight: 800; color: {kpi_fg}; margin-top: 6px;
      }}
      .kpi-sub {{
        font-size: 12px; color: {mute}; margin-top: 4px;
      }}
      .kpi-pill {{
        position:absolute; top: 12px; right: 12px;
        font-size: 12px; padding: 6px 10px; border-radius: 999px;
        background: rgba(34,197,94,.12); color: #22c55e; border:1px solid rgba(34,197,94,.25);
      }}
      .kpi-pill.neg {{ background: rgba(244,63,94,.12); color:#f43f5e; border-color: rgba(244,63,94,.25); }}
      .kpi-link {{
        position:absolute; bottom: 10px; right: 14px; opacity:.5; font-size:12px;
      }}
    </style>
    """, unsafe_allow_html=True)
