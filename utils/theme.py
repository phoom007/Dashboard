# utils/theme.py
import streamlit as st
def set_base_page_config():
    st.set_page_config(page_title="OTOP Sales Dashboard", page_icon="🛍️", layout="wide")
def get_plotly_template():
    return "plotly_white"
def inject_global_css():
    # พื้นหลังแอปขาวตลอด + KPI สไตล์สีสดแบบการ์ดในภาพ
    st.markdown("""
    <style>
      html, body, [data-testid="stAppViewContainer"]{ background:#ffffff; color:#1f2937; }
      .block-container { padding-top: 0.6rem; }

      /* ===== KPI GRID ===== */
      .kpi-grid{
        display:grid; gap:16px; margin:10px 0 18px 0;
        grid-template-columns: repeat(4, minmax(0,1fr));
      }
      @media (max-width:1400px){ .kpi-grid{ grid-template-columns: repeat(2, minmax(0,1fr)); } }
      @media (max-width:700px){ .kpi-grid{ grid-template-columns: 1fr; } }

      /* ===== KPI CARD BASE ===== */
      .kpi-card{
        position:relative; border-radius:20px; padding:18px 18px 16px;
        color:#fff; overflow:hidden; isolation:isolate;
        box-shadow:0 14px 28px rgba(0,0,0,.12);
        transition:transform .15s ease, box-shadow .2s ease, filter .2s ease;
      }
      .kpi-card:hover{ transform: translateY(-2px); box-shadow:0 18px 36px rgba(0,0,0,.18); }
      .kpi-icon{
        width:46px; height:46px; border-radius:12px; background:rgba(255,255,255,.18);
        display:flex; align-items:center; justify-content:center; font-size:22px;
        margin-bottom:10px; backdrop-filter: blur(2px);
      }
      .kpi-value{ font-size:28px; font-weight:800; line-height:1.1; }
      .kpi-title{ font-size:12px; opacity:.95; font-weight:600; letter-spacing:.25px; margin-top:4px; }
      .kpi-sub{ font-size:12px; opacity:.85; margin-top:6px; }

      /* Pills (บวก/ลบ) */
      .kpi-pill{
        position:absolute; top:12px; right:12px; font-size:12px;
        padding:6px 10px; border-radius:999px; background:rgba(255,255,255,.2); backdrop-filter:blur(4px);
        border:1px solid rgba(255,255,255,.25);
      }
      .kpi-pill.pos{ background:rgba(34,197,94,.25); border-color:rgba(34,197,94,.35); }
      .kpi-pill.neg{ background:rgba(244,63,94,.25); border-color:rgba(244,63,94,.35); }

      /* ===== สีสไตล์ (เหมือนภาพ) – ไล่เฉดนุ่ม ๆ ===== */
      .kpi--purple { background:linear-gradient(180deg,#8b5cf6,#7c3aed); }
      .kpi--blue   { background:linear-gradient(180deg,#60a5fa,#3b82f6); }
      .kpi--pink   { background:linear-gradient(180deg,#fb7185,#f43f5e); }
      .kpi--cyan   { background:linear-gradient(180deg,#22d3ee,#06b6d4); }
      .kpi--green  { background:linear-gradient(180deg,#86efac,#22c55e); }
      .kpi--peach  { background:linear-gradient(180deg,#fed7aa,#fb923c); color:#1f2937; }
      .kpi--peach .kpi-icon{ background:rgba(255,255,255,.5); }

      /* ===== Night mode: เปลี่ยนเฉพาะ KPI ให้ดรอปลงเล็กน้อย (พื้นหลังหน้าอื่นยังขาว) ===== */
      .night .kpi-card{ filter:brightness(.92) saturate(.95); box-shadow:0 14px 34px rgba(2,6,23,.28); }
    </style>
    """, unsafe_allow_html=True)

    # ใส่คลาส .night ให้ <body> เมื่อเปิด Night (ไม่แตะพื้นหลัง)
    night = st.session_state.get("display_mode", "Day") == "Night"
    st.markdown(f"""
    <script>
      const root = window.parent.document.querySelector('body');
      if (root) {{
        root.classList.toggle('night', {str(night).lower()});
      }}
    </script>
    """, unsafe_allow_html=True)
