# components/kpi_card.py
# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from utils.formatters import fmt_baht

def _find_prev_month(months: list, current: str):
    """หาชื่อเดือนก่อนหน้า (ตรงกับคอลัมน์ใน df1)"""
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
    """
    แสดง KPI Cards 4 ใบตามชุด (1)(2)(3)(6)(7) โดยจับคู่ 4 ใบแรก:
      1) ยอดขายรวมทั้งประเทศ
      2) จังหวัดขายสูงสุด
      3) สัดส่วนออนไลน์ (ในประเทศ+ต่างประเทศ ออนไลน์ / รวมทุกช่องทาง)
      6) การเติบโต MoM (ยอดรวมทั้งประเทศ)
      7) จังหวัดเติบโตเร็วสุด MoM — แสดงเป็นแคปชันในใบที่ 4 ร่วม
    """
    months = [c for c in df1.columns]  # ลำดับเดือนในตาราง
    prev_month = _find_prev_month(months, selected_month)

    # ---- (1) ยอดขายรวมทั้งประเทศ
    total_cur = float(df1[selected_month].sum())
    total_prev = float(df1[prev_month].sum()) if prev_month else None
    mom = _growth_rate(total_cur, total_prev)

    # ---- (2) จังหวัดขายสูงสุด
    top_province = df1[selected_month].idxmax()
    top_province_sales = float(df1[selected_month].max())

    # ---- (3) สัดส่วนออนไลน์ (รวมออนไลน์ทั้งใน/ต่างประเทศ)
    # จาก df2 (index เป็น 'เดือน' เช่น 'กันยายน 2567')
    month_key = selected_month.split(' ')[0]
    idx_match = next((idx for idx in df2.index if str(idx).startswith(month_key)), None)
    online_ratio = 0.0
    if idx_match:
        row = df2.loc[idx_match]
        online = float(row.get('ในประเทศ(ออนไลน์)', 0.0)) + float(row.get('ต่างประเทศ(ออนไลน์)', 0.0))
        total_chan = float(row.sum()) if row.sum() else 1.0
        online_ratio = (online / total_chan) * 100.0

    # ---- (7) จังหวัดเติบโตเร็วสุด MoM
    fastest_name, fastest_rate = "-", 0.0
    if prev_month:
        # คำนวณ growth rate ต่อจังหวัด
        prev_series = df1[prev_month].replace(0, pd.NA)
        growth = ((df1[selected_month] - df1[prev_month]) / prev_series) * 100.0
        growth = growth.dropna()
        if not growth.empty:
            fastest_name = growth.idxmax()
            fastest_rate = float(growth.max())

    # ===== Render =====
    st.markdown('<div class="kpi-grid">', unsafe_allow_html=True)

    # Card 1 — ยอดขายรวมประเทศ
    st.markdown(f"""
      <div class="kpi-card">
        <div class="kpi-title"><span class="kpi-ic">🛒</span>ยอดขายรวมทั้งประเทศ</div>
        <div class="kpi-value">฿{total_cur:,.0f}</div>
        <div class="kpi-sub">สำหรับเดือน {selected_month}</div>
      </div>
    """, unsafe_allow_html=True)

    # Card 2 — จังหวัดขายสูงสุด
    st.markdown(f"""
      <div class="kpi-card">
        <div class="kpi-title"><span class="kpi-ic">🏆</span>จังหวัดขายสูงสุด</div>
        <div class="kpi-value">{top_province}</div>
        <div class="kpi-sub">ยอดขาย ฿{top_province_sales:,.0f}</div>
      </div>
    """, unsafe_allow_html=True)

    # Card 3 — สัดส่วนออนไลน์
    st.markdown(f"""
      <div class="kpi-card">
        <div class="kpi-title"><span class="kpi-ic">🛍️</span>สัดส่วนออนไลน์</div>
        <div class="kpi-value">{online_ratio:,.2f}%</div>
        <div class="kpi-sub">ในประเทศ+ต่างประเทศ (ออนไลน์)</div>
      </div>
    """, unsafe_allow_html=True)

    # Card 4 — การเติบโต MoM + จังหวัดเติบโตเร็วสุด
    pill_class = "kpi-pill" if mom >= 0 else "kpi-pill neg"
    arrow = "▲" if mom >= 0 else "▼"
    st.markdown(f"""
      <div class="kpi-card">
        <div class="{pill_class}">{arrow} {mom:,.2f}%</div>
        <div class="kpi-title"><span class="kpi-ic">📈</span>การเติบโต MoM</div>
        <div class="kpi-value">{mom:,.2f}%</div>
        <div class="kpi-sub">ยอดขายรวมเทียบเดือนก่อนหน้า</div>
        <div class="kpi-sub" style="margin-top:8px;"><b>⚡ จังหวัดเติบโตเร็วสุด:</b> {fastest_name} ({fastest_rate:,.2f}%)</div>
      </div>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
