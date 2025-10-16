# utils/theme.py
# -*- coding: utf-8 -*-
import streamlit as st

def set_base_page_config():
    st.set_page_config(page_title="OTOP Sales Dashboard", page_icon="🛍️", layout="wide")

def get_plotly_template():
    # ใช้ขาวตลอด ทั้ง Day & Night ตามสเปก
    return "plotly_white"

def inject_global_css():
    # พื้นหลังแอป/ตัวอักษรหลัก — ขาวเสมอ, ตัวอักษรเข้มอ่านง่าย
    st.markdown("""
    <style>
      html, body, [data-testid="stAppViewContainer"]{
        background: #ffffff;
        color: #1f2937;
      }
      /* ------- KPI shared ------- */
      .kpi-grid{
        display:grid; gap:18px; margin:8px 0 18px 0;
        grid-template-columns: repeat(4, minmax(0,1fr));
      }
      @media (max-width:1400px){ .kpi-grid{ grid-template-columns: repeat(2, minmax(0,1fr)); } }
      @media (max-width:700px){ .kpi-grid{ grid-template-columns: 1fr; } }

      .kpi-card{ position:relative; border-radius:18px; padding:18px; border:1px solid; transition:transform .15s ease, box-shadow .2s ease, border-color .2s ease; }
      .kpi-card:hover{ transform: translateY(-2px); }

      .kpi-title{ font-weight:600; font-size:14px; letter-spacing:.2px; display:flex; align-items:center; gap:8px; }
      .kpi-value{ font-size:28px; font-weight:800; margin-top:6px; }
      .kpi-sub{ font-size:12px; color:#6b7280; margin-top:4px; }

      .kpi-pill{ position:absolute; top:12px; right:12px; font-size:12px; padding:6px 10px; border-radius:999px; }
      .kpi-pill.pos{ background: rgba(34,197,94,.12); color:#16a34a; border:1px solid rgba(34,197,94,.25); }
      .kpi-pill.neg{ background: rgba(244,63,94,.12); color:#e11d48; border:1px solid rgba(244,63,94,.25); }

      /* ------- KPI Day ------- */
      .kpi-day{
        background: #0f172a; /* slate-900 เข้ม เนี้ยบ */
        color:#e2e8f0;
        border-color: rgba(148,163,184,.22);
        box-shadow: 0 10px 24px rgba(2,6,23,.18);
      }
      .kpi-day .kpi-title{ color:#cbd5e1; }
      .kpi-day .kpi-sub{ color:#94a3b8; }

      /* ------- KPI Night (เฉพาะกล่อง KPI เท่านั้น) ------- */
      .kpi-night{
        background: linear-gradient(180deg, #0b1220, #111827);
        color:#e5e7eb;
        border-color: rgba(148,163,184,.28);
        box-shadow: 0 14px 30px rgba(0,0,0,.35);
      }
      .kpi-night .kpi-title{ color:#cbd5e1; }
      .kpi-night .kpi-sub{ color:#9ca3af; }
    </style>
    """, unsafe_allow_html=True)
