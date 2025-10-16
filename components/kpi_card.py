# components/kpi_card.py
# -*- coding: utf-8 -*-
import streamlit as st
import numpy as np
import pandas as pd

def _find_month_index_like(index, month_text: str):
    for i in index:
        if str(i).startswith(month_text):
            return i
    return None

def render_kpis(df1: pd.DataFrame, df2: pd.DataFrame, df3: pd.DataFrame, selected_month: str) -> None:
    # KPI 1
    total_sales = float(df1[selected_month].sum())
    # KPI 2
    top_province = str(df1[selected_month].idxmax())
    top_province_sales = float(df1[selected_month].max())
    # KPI 3
    month_key = selected_month.split()[0]
    idx_match = _find_month_index_like(df2.index, month_key)
    online_share = 0.0
    if idx_match is not None:
        total_channels = float(df2.loc[idx_match].sum())
        online_sum = 0.0
        for col in df2.columns:
            if "ออนไลน์" in col:
                online_sum += float(df2.loc[idx_match, col])
        if total_channels > 0:
            online_share = (online_sum / total_channels) * 100.0
    # KPI 4 (MoM + fastest province)
    month_cols = [c for c in df1.columns if ("2566" in c or "2567" in c)]
    if not month_cols: month_cols = list(df1.columns)
    try:
        cur_idx = month_cols.index(selected_month)
    except ValueError:
        cur_idx = len(month_cols) - 1
    prev_col = month_cols[cur_idx - 1] if cur_idx - 1 >= 0 else None

    mom_pct = None
    fastest_name = "-"
    fastest_val = None

    if prev_col:
        total_prev = float(df1[prev_col].sum())
        if total_prev > 0:
            mom_pct = (total_sales - total_prev) / total_prev * 100.0
        prev_series = df1[prev_col].replace(0, np.nan)
        growth = (df1[selected_month] - df1[prev_col]) / prev_series * 100.0
        growth = growth.replace([np.inf, -np.inf], np.nan).dropna()
        if not growth.empty:
            fastest_name = str(growth.idxmax())
            fastest_val = float(growth.max())

    pill_html = ""
    if mom_pct is not None:
        if mom_pct >= 0:
            pill_html = f'<div class="kpi-pill pos">▲ {mom_pct:.2f}%</div>'
        else:
            pill_html = f'<div class="kpi-pill neg">▼ {mom_pct:.2f}%</div>'

    html = f"""
    <div class="kpi-row">
      <div class="kpi-card kpi-compact kpi--purple">
        <div class="kpi-top">
          <div class="kpi-icon">🛒</div>
          <div>
            <div class="kpi-value">฿{total_sales:,.0f}</div>
            <div class="kpi-title">ยอดขายรวมทั้งประเทศ</div>
          </div>
        </div>
        <div class="kpi-sub">สำหรับเดือน {selected_month}</div>
      </div>

      <div class="kpi-card kpi-compact kpi--blue">
        <div class="kpi-top">
          <div class="kpi-icon">🏆</div>
          <div>
            <div class="kpi-value">{top_province}</div>
            <div class="kpi-title">จังหวัดขายสูงสุด</div>
          </div>
        </div>
        <div class="kpi-sub">ยอดขาย ฿{top_province_sales:,.0f}</div>
      </div>

      <div class="kpi-card kpi-compact kpi--green">
        <div class="kpi-top">
          <div class="kpi-icon">🛍️</div>
          <div>
            <div class="kpi-value">{online_share:.2f}%</div>
            <div class="kpi-title">สัดส่วนออนไลน์</div>
          </div>
        </div>
        <div class="kpi-sub">ในประเทศ+ต่างประเทศ (ออนไลน์)</div>
      </div>

      <div class="kpi-card kpi-compact kpi--peach">
        {pill_html}
        <div class="kpi-top">
          <div class="kpi-icon">📈</div>
          <div>
            <div class="kpi-value">{(mom_pct if mom_pct is not None else 0):.2f}%</div>
            <div class="kpi-title">การเติบโต MoM</div>
          </div>
        </div>
        <div class="kpi-sub">จังหวัดเติบโตเร็วสุด: {fastest_name}{f" ({fastest_val:.2f}%)" if fastest_val is not None else ""}</div>
      </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
