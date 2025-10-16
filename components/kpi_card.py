# components/kpi_card.py
# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd

def _prev_month(cols, cur):
    try:
        i = list(cols).index(cur)
        return cols[i-1] if i > 0 else None
    except ValueError:
        return None

def _growth(cur, prev):
    if prev is None or prev == 0: return 0.0
    return ((cur - prev) / prev) * 100.0

def render_kpis(df1: pd.DataFrame, df2: pd.DataFrame, df3: pd.DataFrame, selected_month: str):
    months = list(df1.columns)
    prev_m = _prev_month(months, selected_month)

    total_cur = float(df1[selected_month].sum())
    total_prev = float(df1[prev_m].sum()) if prev_m else None
    mom = _growth(total_cur, total_prev)

    top_province = df1[selected_month].idxmax()
    top_province_sales = float(df1[selected_month].max())

    mk = selected_month.split(' ')[0]
    idx = next((i for i in df2.index if str(i).startswith(mk)), None)
    online_ratio = 0.0
    if idx is not None:
        row = df2.loc[idx]
        online = float(row.get('ในประเทศ(ออนไลน์)', 0.0)) + float(row.get('ต่างประเทศ(ออนไลน์)', 0.0))
        total_chan = float(row.sum()) if row.sum() else 1.0
        online_ratio = (online / total_chan) * 100.0

    fastest_name, fastest_rate = "-", 0.0
    if prev_m:
        prev_series = df1[prev_m].replace(0, pd.NA)
        gr = ((df1[selected_month] - df1[prev_m]) / prev_series) * 100.0
        gr = gr.dropna()
        if not gr.empty:
            fastest_name = gr.idxmax()
            fastest_rate = float(gr.max())

    arrow = "▲" if mom >= 0 else "▼"
    pill_cls = "kpi-pill pos" if mom >= 0 else "kpi-pill neg"

    cards = [
        {
            "cls": "kpi-card kpi-compact kpi--purple",
            "icon": "🛒",
            "value": f"฿{total_cur:,.0f}",
            "title": "ยอดขายรวมทั้งประเทศ",
            "sub": f"สำหรับเดือน {selected_month}",
            "pill": None,
        },
        {
            "cls": "kpi-card kpi-compact kpi--blue",
            "icon": "🏆",
            "value": f"{top_province}",
            "title": "จังหวัดขายสูงสุด",
            "sub": f"ยอดขาย ฿{top_province_sales:,.0f}",
            "pill": None,
        },
        {
            "cls": "kpi-card kpi-compact kpi--green",
            "icon": "🛍️",
            "value": f"{online_ratio:,.2f}%",
            "title": "สัดส่วนออนไลน์",
            "sub": "ในประเทศ+ต่างประเทศ (ออนไลน์)",
            "pill": None,
        },
        {
            "cls": "kpi-card kpi-compact kpi--peach",
            "icon": "📈",
            "value": f"{mom:,.2f}%",
            "title": "การเติบโต MoM",
            "sub": f"จังหวัดเติบโตเร็วสุด: {fastest_name} ({fastest_rate:,.2f}%)" if fastest_name!="-" else "เปรียบเทียบกับเดือนก่อนหน้า",
            "pill": {"text": f"{arrow} {mom:,.2f}%", "cls": pill_cls},
        },
    ]

    st.markdown('<div class="kpi-row">', unsafe_allow_html=True)
    for c in cards:
        pill_html = f'<div class="{c["pill"]["cls"]}">{c["pill"]["text"]}</div>' if c.get("pill") else ""
        st.markdown(f"""
          <div class="{c['cls']}">
            {pill_html}
            <div class="kpi-top">
              <div class="kpi-icon">{c['icon']}</div>
              <div>
                <div class="kpi-value">{c['value']}</div>
                <div class="kpi-title">{c['title']}</div>
              </div>
            </div>
            <div class="kpi-sub">{c['sub']}</div>
          </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

