# components/kpi_card.py
# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd

def _find_prev_month(months: list, current: str):
    try:
        idx = months.index(current)
        return months[idx-1] if idx > 0 else None
    except ValueError:
        return None

def _growth_rate(cur: float, prev: float) -> float:
    if prev is None or prev == 0:
        return 0.0
    return ((cur - prev) / prev) * 100.0

def render_kpis(df1: pd.DataFrame, df2: pd.DataFrame, df3: pd.DataFrame, selected_month: str):
    months = list(df1.columns)
    prev_month = _find_prev_month(months, selected_month)

    # (1) total
    total_cur = float(df1[selected_month].sum())
    total_prev = float(df1[prev_month].sum()) if prev_month else None
    mom = _growth_rate(total_cur, total_prev)

    # (2) top province
    top_province = df1[selected_month].idxmax()
    top_province_sales = float(df1[selected_month].max())

    # (3) online ratio
    month_key = selected_month.split(' ')[0]
    idx_match = next((idx for idx in df2.index if str(idx).startswith(month_key)), None)
    online_ratio = 0.0
    if idx_match is not None:
        row = df2.loc[idx_match]
        online = float(row.get('ในประเทศ(ออนไลน์)', 0.0)) + float(row.get('ต่างประเทศ(ออนไลน์)', 0.0))
        total_chan = float(row.sum()) if row.sum() else 1.0
        online_ratio = (online / total_chan) * 100.0

    # (7) fastest MoM province
    fastest_name, fastest_rate = "-", 0.0
    if prev_month:
        prev_series = df1[prev_month].replace(0, pd.NA)
        growth = ((df1[selected_month] - df1[prev_month]) / prev_series) * 100.0
        growth = growth.dropna()
        if not growth.empty:
            fastest_name = growth.idxmax()
            fastest_rate = float(growth.max())

    # เลือกโหมดของ KPI card
    is_night = (st.session_state.get("display_mode", "Day") == "Night")
    kpi_class = "kpi-card kpi-night" if is_night else "kpi-card kpi-day"
    pill_class = "kpi-pill pos" if mom >= 0 else "kpi-pill neg"
    arrow = "▲" if mom >= 0 else "▼"

    st.markdown('<div class="kpi-grid">', unsafe_allow_html=True)

    st.markdown(f"""
      <div class="{kpi_class}">
        <div class="kpi-title">🛒 ยอดขายรวมทั้งประเทศ</div>
        <div class="kpi-value">฿{total_cur:,.0f}</div>
        <div class="kpi-sub">สำหรับเดือน {selected_month}</div>
      </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
      <div class="{kpi_class}">
        <div class="kpi-title">🏆 จังหวัดขายสูงสุด</div>
        <div class="kpi-value">{top_province}</div>
        <div class="kpi-sub">ยอดขาย ฿{top_province_sales:,.0f}</div>
      </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
      <div class="{kpi_class}">
        <div class="kpi-title">🛍️ สัดส่วนออนไลน์</div>
        <div class="kpi-value">{online_ratio:,.2f}%</div>
        <div class="kpi-sub">ในประเทศ+ต่างประเทศ (ออนไลน์)</div>
      </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
      <div class="{kpi_class}">
        <div class="{pill_class}">{arrow} {mom:,.2f}%</div>
        <div class="kpi-title">📈 การเติบโต MoM</div>
        <div class="kpi-value">{mom:,.2f}%</div>
        <div class="kpi-sub">ยอดขายรวมเทียบเดือนก่อนหน้า</div>
        <div class="kpi-sub" style="margin-top:8px;"><b>⚡ จังหวัดเติบโตเร็วสุด:</b> {fastest_name} ({fastest_rate:,.2f}%)</div>
      </div>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
