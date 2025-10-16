# components/charts.py
# -*- coding: utf-8 -*-
import streamlit as st
import plotly.express as px
import pandas as pd

def _unique_suffix(prefix: str) -> str:
    """คืน suffix ไม่ซ้ำสำหรับ prefix นั้นๆ ในหนึ่งรอบ render"""
    if "_ctrl_counts" not in st.session_state:
        st.session_state._ctrl_counts = {}
    cnt = st.session_state._ctrl_counts.get(prefix, 0) + 1
    st.session_state._ctrl_counts[prefix] = cnt
    return f"{prefix}_{cnt}"

def render_time_kind_controls(prefix="main"):
    """ตัวเลือกแบบเลื่อนสำหรับช่วงเวลาและชนิดกราฟ (auto-unique key)"""
    # state หลักของค่าที่เลือก (ค่านี้คงอยู่ข้ามคีย์ของ widget)
    if "time_range" not in st.session_state:
        st.session_state.time_range = "ALL"
    if "bar_kind" not in st.session_state:
        st.session_state.bar_kind = "Stacked"

    # ป้องกัน key ซ้ำโดยเพิ่ม suffix ที่ไม่ซ้ำต่อการเรียก
    suffix = _unique_suffix(prefix)

    c1, c2 = st.columns([1, 1], gap="small")
    with c1:
        st.caption("ช่วงเวลา")
        st.session_state.time_range = st.select_slider(
            label="",
            options=["ALL", "1M", "6M", "1Y"],
            value=st.session_state.time_range,
            key=f"time_range_slider_{suffix}",  # <-- ไม่ซ้ำแล้ว
        )
    with c2:
        st.caption("ชนิดกราฟ")
        st.session_state.bar_kind = st.select_slider(
            label="",
            options=["Stacked", "Clustered"],
            value=st.session_state.bar_kind,
            key=f"bar_kind_slider_{suffix}",    # <-- ไม่ซ้ำแล้ว
        )

def render_main_row_charts(df1, df2, selected_month, plotly_template="plotly_white", key_prefix="main"):
    tail_map = {"ALL": len(df2), "1M": 1, "6M": 6, "1Y": 12}
    n_tail = tail_map.get(st.session_state.get("time_range", "ALL"), len(df2))
    barmode = "stack" if st.session_state.get("bar_kind", "Stacked") == "Stacked" else "group"

    data = df2.reset_index().tail(n_tail)
    long_df = data.melt(id_vars="เดือน", var_name="ช่องทาง", value_name="value")

    left, right = st.columns([3, 2], gap="large")

    with left:
        st.subheader("โครงสร้างช่องทางตามช่วงเวลา")
        fig = px.bar(
            long_df, x="เดือน", y="value", color="ช่องทาง",
            barmode=barmode, template=plotly_template, labels={"value": "บาท (฿)"}
        )
        fig.update_traces(texttemplate="%{y:,.0f}", textposition="outside", cliponaxis=False)
        fig.update_layout(margin=dict(l=0, r=0, b=0, t=10), legend_title_text="")
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False}, key=f"main_bar_{key_prefix}")

    with right:
        st.subheader(f"20 จังหวัดยอดขายสูงสุด ({selected_month})")
        monthly_data = df1[[selected_month]].sort_values(by=selected_month, ascending=False).reset_index()
        bar = px.bar(
            monthly_data.head(20).sort_values(by=selected_month, ascending=True),
            x=selected_month, y="จังหวัด", orientation="h",
            template=plotly_template, labels={"จังหวัด": "", selected_month: "ยอดขาย (บาท)"},
            height=600
        )
        bar.update_layout(yaxis={'categoryorder': 'total ascending'}, margin=dict(l=0, r=0, b=0, t=10))
        st.plotly_chart(bar, use_container_width=True, config={"displayModeBar": False}, key=f"top20_{key_prefix}")

def render_revenue_sources(df2, selected_month, plotly_template="plotly_white", key_prefix="revsrc"):
    st.markdown("#### Revenue Sources (เดือนเดียว)")
    month_key = selected_month.split(" ")[0]
    idx = next((i for i in df2.index if str(i).startswith(month_key)), None)
    if idx is None:
        st.info("ไม่พบข้อมูลสำหรับเดือนนี้", icon="ℹ️")
        return
    s = df2.loc[idx]
    fig = px.pie(values=s.values, names=s.index, hole=.45, template=plotly_template)
    fig.update_layout(margin=dict(l=0, r=0, b=0, t=0), legend_title_text="")
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False}, key=f"pie_{key_prefix}")

def render_cdd_sources_embeds(key_prefix="cdd"):
    st.markdown("#### แหล่งข้อมูลที่ใช้สร้าง Dashboard (ฝังจาก CDD)")
    url_map = {
        "otop_r06": "https://logi.cdd.go.th/otop/cdd_report/otop_r06.php?year=2567",
        "otop_r05": "https://logi.cdd.go.th/otop/cdd_report/otop_r05.php?year=2567",
        "otop_r04": "https://logi.cdd.go.th/otop/cdd_report/otop_r04.php?year=2567&org_group=0",
    }
    key = st.selectbox(
        "เลือกหน้า",
        options=list(url_map.keys()),
        format_func=lambda k: k.upper(),
        key=f"cdd_select_{key_prefix}",   # ← key ให้ selectbox ได้เหมือนเดิม
    )
    # 👇 เอา key ออกจาก iframe (Streamlit ไม่รองรับ)
    st.components.v1.iframe(url_map[key], height=420, scrolling=True)
