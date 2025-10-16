def inject_global_css():
    st.markdown("""
    <style>
      html, body, [data-testid="stAppViewContainer"]{ background:#ffffff; color:#1f2937; }
      .block-container { padding-top: .6rem; }

      /* ===== KPI GRID =====
         Desktop: 4 ใบในแถวเดียวเท่ากัน
         <= 1024px: 2 ใบ/แถว
      */
      .kpi-grid{
        display:grid;
        grid-template-columns: repeat(4, minmax(0,1fr));
        gap:14px;
        margin:10px 0 18px 0;
      }
      @media (max-width:1024px){
        .kpi-grid{ grid-template-columns: repeat(2, minmax(0,1fr)); }
      }

      /* ===== KPI CARD BASE ===== */
      .kpi-card{
        position:relative; border-radius:14px; padding:14px;
        color:#fff; overflow:hidden; isolation:isolate;
        box-shadow:0 10px 20px rgba(0,0,0,.10);
        transition:transform .12s ease, box-shadow .2s ease, filter .2s ease;
      }
      .kpi-card:hover{ transform: translateY(-2px); box-shadow:0 14px 30px rgba(0,0,0,.16); }

      /* Compact layout: ทำให้ทุกใบสูงเท่ากันและอ่านชัด */
      .kpi-compact{ min-height:130px; display:flex; flex-direction:column; justify-content:space-between; }
      .kpi-compact .kpi-top{ display:flex; align-items:center; gap:10px; }
      .kpi-compact .kpi-icon{ width:38px; height:38px; border-radius:10px; background:rgba(255,255,255,.18);
                               display:flex; align-items:center; justify-content:center; font-size:18px; }
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

      /* พาเล็ตสี */
      .kpi--purple { background:linear-gradient(180deg,#8b5cf6,#7c3aed); }
      .kpi--blue   { background:linear-gradient(180deg,#60a5fa,#3b82f6); }
      .kpi--green  { background:linear-gradient(180deg,#86efac,#22c55e); }
      .kpi--peach  { background:linear-gradient(180deg,#fed7aa,#fb923c); color:#1f2937; }
      .kpi--peach .kpi-icon{ background:rgba(255,255,255,.6); }

      /* Night mode เฉพาะ KPI */
      .night .kpi-card{ filter:brightness(.92) saturate(.95); box-shadow:0 12px 28px rgba(2,6,23,.26); }
    </style>
    """, unsafe_allow_html=True)

    night = st.session_state.get("display_mode", "Day") == "Night"
    st.markdown(f"""
    <script>
      const root = window.parent.document.querySelector('body');
      if (root) root.classList.toggle('night', {str(night).lower()});
    </script>
    """, unsafe_allow_html=True)
