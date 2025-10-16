import streamlit as st
import pandas as pd
from utils.formatters import fmt_baht, fmt_pct

def _mom_change(series: pd.Series, month: str):
    idx = list(series.index).index(month)
    if idx == 0: 
        return None
    prev = series.iloc[idx-1]
    cur = series.iloc[idx]
    if prev == 0: 
        return None
    return (cur - prev) / prev

def render_kpis(df1, df2, df3, selected_month: str):
    total_sales_month = df1[selected_month].sum()
    top_province = df1[selected_month].idxmax()
    top_province_sales = df1[selected_month].max()

    # Online Share % (ในปท.ออนไลน์ + ตปท.ออนไลน์) / รวม
    month_key = selected_month.split(' ')[0]
    idx_match = next((idx for idx in df2.index if str(idx).startswith(month_key)), None)
    online_share = None
    if idx_match:
        sub = df2.loc[idx_match]
        online = sub.get("ในประเทศ(ออนไลน์)", 0) + sub.get("ต่างประเทศ(ออนไลน์)", 0)
        total_channel = sub.sum()
        online_share = (online / total_channel) if total_channel else None

    # Total Sales MoM %
    national_series = df1.sum(axis=0)  # รวมทุกจังหวัดรายเดือน
    ts_mom = _mom_change(national_series, selected_month)

    # Fastest Growing Province (MoM)
    best_name, best_val = None, None
    for prov in df1.index:
        mom = _mom_change(df1.loc[prov], selected_month)
        if mom is None:
            continue
        if (best_val is None) or (mom > best_val):
            best_val = mom
            best_name = prov

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        _card("💰 ยอดขายรวมทั้งประเทศ", fmt_baht(total_sales_month), f"สำหรับเดือน {selected_month}")
    with col2:
        _card("🏆 จังหวัดขายสูงสุด", top_province, f"ยอดขาย {fmt_baht(top_province_sales)}")
    with col3:
        _card("🛒 สัดส่วนออนไลน์", fmt_pct(online_share), "ในประเทศ+ต่างประเทศ (ออนไลน์)")
    with col4:
        _card("📈 การเติบโต MoM", fmt_pct(ts_mom), "ยอดขายรวมเทียบเดือนก่อน")
    with col5:
        _card("⚡ จังหวัดเติบโตเร็วสุด (MoM)", best_name or "-", fmt_pct(best_val) if best_val is not None else "—")

def _card(title, value, subtitle):
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">{title}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-delta">{subtitle}</div>
    </div>
    """, unsafe_allow_html=True)
