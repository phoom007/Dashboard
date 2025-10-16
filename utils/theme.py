# utils/theme.py
# -*- coding: utf-8 -*-
import streamlit as st

def set_base_page_config() -> None:
    st.set_page_config(
        page_title="OTOP Dashboard",
        page_icon="🛍️",
        layout="wide",
        initial_sidebar_state="expanded",
    )

def inject_global_css() -> None:
    st.markdown(
        """
<style>
  /* base */
  html, body, [data-testid="stAppViewContainer"]{
      background:#ffffff !important;
      color:#1f2937;
      font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, "Helvetica Neue", Arial, "Noto Sans",
                   "Liberation Sans", "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol";
  }
  .block-container{ padding-top:.6rem; }

  /* -------- Premium Tabs -------- */
  /* ทำให้แท็บดูเป็นเม็ดแคปซูล */
  [data-baseweb="tab-list"]{
      background:#f8fafc;
      padding:8px;
      border-radius:14px;
      gap:8px;
      border:1px solid #e5e7eb;
  }
  [data-baseweb="tab"]{
      background:#ffffff;
      border:1px solid #e5e7eb;
      border-radius:12px;
      box-shadow:0 1px 0 rgba(0,0,0,.02);
      padding:10px 14px;
      font-weight:700;
      color:#111827;
  }
  [aria-selected="true"][data-baseweb="tab"]{
      background:linear-gradient(180deg,#eef2ff,#dbeafe);
      border-color:#bfdbfe;
      box-shadow:0 6px 16px rgba(59,130,246,.15);
      color:#1d4ed8;
  }

  /* -------- Pill Radios (ALL/1M/6M/1Y / Stacked/Clustered) -------- */
  .pill-group{
      display:flex; gap:8px; flex-wrap:wrap; align-items:center;
  }
  .pill{
      border:1px solid #e5e7eb; border-radius:999px; padding:8px 14px;
      background:#fff; cursor:pointer; user-select:none;
      font-weight:600; font-size:13px;
      transition:all .15s ease;
  }
  .pill:hover{ box-shadow:0 2px 12px rgba(0,0,0,.08) }
  .pill.is-active{
      background:linear-gradient(180deg,#eef2ff,#dbeafe);
      border-color:#bfdbfe; color:#1d4ed8;
      box-shadow:0 6px 16px rgba(59,130,246,.15);
  }
  /* ซ่อน radio จริง ๆ ของ Streamlit แล้วใช้ปุ่มแทน */
  .hide-radio > div[data-baseweb="radio"]{ display:none; }

  /* -------- Extras -------- */
  .section-title{ font-weight:800; font-size:20px; margin:2px 0 8px 0; }
  .subtle{ color:#6b7280; font-size:13px }
</style>
        """,
        unsafe_allow_html=True,
    )

def get_plotly_template() -> str:
    return "plotly_white"
