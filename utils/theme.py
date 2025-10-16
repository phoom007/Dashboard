# utils/theme.py
# -*- coding: utf-8 -*-
"""
ธีม / สไตล์กลางของแอป Streamlit

สิ่งที่มีให้ใช้:
- set_base_page_config(): ตั้งค่าเพจพื้นฐาน (ชื่อหน้า, ไอคอน, layout)
- inject_global_css(): ฉีด CSS ทั้งหมด (พื้นหลังขาว, KPI row แบบ 4 กล่องบรรทัดเดียว,
                      สวิตช์ Night จะทำให้ KPI มืดลงเล็กน้อยเท่านั้น)
- get_plotly_template(): ส่งคืน "plotly_white" ให้กราฟใช้โทนสว่างเสมอ
"""
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
  /* พื้นหลังและฟอนต์ทั่วไป */
  html, body, [data-testid="stAppViewContainer"]{
      background:#ffffff !important;
      color:#1f2937;
      font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, "Helvetica Neue", Arial, "Noto Sans",
                   "Liberation Sans", "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol";
  }
  .block-container{ padding-top:.6rem; }

  /* ลิงก์ */
  a, .stMarkdown a{ color:#2563eb; text-decoration:none; }
  a:hover{ text-decoration:underline; }

  /* เส้นคั่นที่บางหน่อย */
  hr, .stDivider{ opacity:.9; }

  /* ---------- KPI ROW (4 กล่องบรรทัดเดียว) ---------- */
  .kpi-row{
      display:flex; gap:14px; margin:10px 0 18px 0;
      overflow-x:auto; padding-bottom:4px; scrollbar-width:thin;
  }
  .kpi-row::-webkit-scrollbar{ height:8px }
  .kpi-row::-webkit-scrollbar-thumb{ background:#e5e7eb; border-radius:999px }

  .kpi-card{
      position:relative; border-radius:14px; padding:14px;
      color:#fff; overflow:hidden; isolation:isolate;
      box-shadow:0 10px 20px rgba(0,0,0,.10);
      transition:transform .12s ease, box-shadow .2s ease, filter .2s ease;
      flex:0 0 calc(25% - 10.5px);   /* 4 ใบ/บรรทัด */
      min-width:280px;
  }
  @media (min-width:1280px){
      .kpi-card{ min-width:0; }
  }
  .kpi-card:hover{ transform: translateY(-2px); box-shadow:0 14px 30px rgba(0,0,0,.16); }

  .kpi-compact{ min-height:130px; display:flex; flex-direction:column; justify-content:space-between; }
  .kpi-compact .kpi-top{ display:flex; align-items:center; gap:10px; }
  .kpi-compact .kpi-icon{
      width:38px; height:38px; border-radius:10px;
      background:rgba(255,255,255,.18);
      display:flex; align-items:center; justify-content:center;
      font-size:18px;
  }
  .kpi-compact .kpi-value{ font-size:22px; font-weight:800; line-height:1.1; }
  .kpi-compact .kpi-title{ font-size:12px; font-weight:600; opacity:.95; }
  .kpi-compact .kpi-sub{ font-size:11px; opacity:.85; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }

  .kpi-pill{
      position:absolute; top:10px; right:10px; font-size:11px;
      padding:5px 9px; border-radius:999px; background:rgba(255,255,255,.2);
      border:1px solid rgba(255,255,255,.25); backdrop-filter:blur(4px);
  }
  .kpi-pill.pos{ background:rgba(34,197,94,.25); border-color:rgba(34,197,94,.35); }
  .kpi-pill.neg{ background:rgba(244,63,94,.25); border-color:rgba(244,63,94,.35); }

  /* พาเล็ตสีของคาร์ด */
  .kpi--purple { background:linear-gradient(180deg,#8b5cf6,#7c3aed); }
  .kpi--blue   { background:linear-gradient(180deg,#60a5fa,#3b82f6); }
  .kpi--green  { background:linear-gradient(180deg,#86efac,#22c55e); }
  .kpi--peach  { background:linear-gradient(180deg,#fed7aa,#fb923c); color:#1f2937; }
  .kpi--peach .kpi-icon{ background:rgba(255,255,255,.6); }

  /* --------- Night mode เฉพาะ KPI (พื้นหลังทั้งแอปยังขาว) --------- */
  body.night .kpi-card{
      filter:brightness(.92) saturate(.95);
      box-shadow:0 12px 28px rgba(2,6,23,.26);
  }
</style>
        """,
        unsafe_allow_html=True,
    )

    # toggle class .night ตาม st.session_state.display_mode
    night = st.session_state.get("display_mode", "Day") == "Night"
    st.markdown(
        f"""
<script>
  (function(){{
    const root = window.parent.document.querySelector('body');
    if (!root) return;
    root.classList.toggle('night', {str(night).lower()});
  }})();
</script>
        """,
        unsafe_allow_html=True,
    )


def get_plotly_template() -> str:
    return "plotly_white"
