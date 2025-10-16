# components/charts.py
# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from typing import List

# ------------------------------
# Controls (ช่วงเวลา / ชนิดกราฟ)
# ------------------------------
def _unique_suffix(prefix: str) -> str:
    """คืน suffix ไม่ซ้ำสำหรับ prefix นั้นๆ ในหนึ่งรอบ render"""
    if "_ctrl_counts" not in st.session_state:
        st.session_state._ctrl_counts = {}
    cnt = st.session_state._ctrl_counts.get(prefix, 0) + 1
    st.session_state._ctrl_counts[prefix] = cnt
    return f"{prefix}_{cnt}"

def render_time_kind_controls(prefix="main"):
    """ตัวเลือกแบบเลื่อนสำหรับช่วงเวลาและชนิดกราฟ (auto-unique key)"""
    if "time_range" not in st.session_state:
        st.session_state.time_range = "ALL"
    if "bar_kind" not in st.session_state:
        st.session_state.bar_kind = "Stacked"

    suffix = _unique_suffix(prefix)

    c1, c2 = st.columns([1, 1], gap="small")
    with c1:
        st.caption("ช่วงเวลา")
        st.session_state.time_range = st.select_slider(
            label="",
            options=["ALL", "1M", "6M", "1Y"],
            value=st.session_state.time_range,
            key=f"time_range_slider_{suffix}",
        )
    with c2:
        st.caption("ชนิดกราฟ")
        st.session_state.bar_kind = st.select_slider(
            label="",
            options=["Stacked", "Clustered"],
            value=st.session_state.bar_kind,
            key=f"bar_kind_slider_{suffix}",
        )

# ------------------------------
# กราฟหลักแถวแรก
# ------------------------------
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

# ------------------------------
# Revenue Sources (เดือนเดียว)
# ------------------------------
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

# ------------------------------
# ฝังหน้าเว็บ CDD (ไม่รองรับ key ใน iframe)
# ------------------------------
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
        key=f"cdd_select_{key_prefix}",
    )
    st.components.v1.iframe(url_map[key], height=420, scrolling=True)

# ======================================================
# NEW: Regional Growth Trend & Product Category Charts
# ======================================================

# แผนที่จังหวัด -> ภูมิภาค (6 ภูมิภาคมาตรฐาน)
_REGION_MAP = {
    "ภาคเหนือ": [
        "เชียงใหม่","เชียงราย","ลำพูน","ลำปาง","แพร่","น่าน","พะเยา","แม่ฮ่องสอน","อุตรดิตถ์","ตาก","สุโขทัย","พิษณุโลก","พิจิตร","เพชรบูรณ์"
    ],
    "ภาคตะวันออกเฉียงเหนือ": [
        "ขอนแก่น","อุดรธานี","เลย","หนองคาย","หนองบัวลำภู","ชัยภูมิ","นครราชสีมา","บุรีรัมย์","สุรินทร์","ศรีสะเกษ",
        "อุบลราชธานี","ยโสธร","อำนาจเจริญ","มหาสารคาม","ร้อยเอ็ด","กาฬสินธุ์","สกลนคร","นครพนม","มุกดาหาร","บึงกาฬ"
    ],
    "ภาคกลาง": [
        "นนทบุรี","ปทุมธานี","พระนครศรีอยุธยา","สระบุรี","อ่างทอง","ลพบุรี","สิงห์บุรี","ชัยนาท",
        "นครสวรรค์","อุทัยธานี","กำแพงเพชร"
    ],
    "ภาคตะวันออก": ["ชลบุรี","ระยอง","จันทบุรี","ตราด","ฉะเชิงเทรา","ปราจีนบุรี","นครนายก","สระแก้ว"],
    "ภาคตะวันตก": ["ราชบุรี","กาญจนบุรี","สุพรรณบุรี","นครปฐม","สมุทรสาคร","สมุทรสงคราม","เพชรบุรี","ประจวบคีรีขันธ์"],
    "ภาคใต้": [
        "นครศรีธรรมราช","สุราษฎร์ธานี","ชุมพร","ระนอง","พังงา","ภูเก็ต","กระบี่","ตรัง","พัทลุง","สงขลา","สตูล","ปัตตานี","ยะลา","นราธิวาส"
    ],
}

def _build_regional_df(df1: pd.DataFrame, month_cols: List[str]) -> pd.DataFrame:
    """สรุปยอดขายเป็นราย 'ภูมิภาค' ต่อเดือน"""
    frames = []
    for region, provs in _REGION_MAP.items():
        prov_in_df = [p for p in provs if p in df1.index]
        if not prov_in_df:
            continue
        s = df1.loc[prov_in_df, month_cols].sum()
        frames.append(pd.DataFrame({"ภูมิภาค": region, "เดือน": month_cols, "ยอดขาย": s.values}))
    if not frames:
        return pd.DataFrame(columns=["ภูมิภาค","เดือน","ยอดขาย"])
    return pd.concat(frames, ignore_index=True)

def render_regional_growth(df1, month_cols, selected_month, plotly_template="plotly_white", key_prefix="regional"):
    st.subheader("การเติบโตยอดขายตามภูมิภาค (Regional Growth)")
    reg = _build_regional_df(df1, month_cols)
    if reg.empty:
        st.info("ไม่มีข้อมูลภูมิภาคเพียงพอ", icon="ℹ️")
        return

    # หา index ของเดือนที่เลือก เพื่อคำนวณ MoM
    try:
        m_idx = month_cols.index(selected_month)
    except ValueError:
        m_idx = len(month_cols) - 1
    prev_idx = max(0, m_idx - 1)
    month_now, month_prev = month_cols[m_idx], month_cols[prev_idx]

    # คำนวณ MoM ต่อภูมิภาค
    cur = reg[reg["เดือน"] == month_now].set_index("ภูมิภาค")["ยอดขาย"]
    prev = reg[reg["เดือน"] == month_prev].set_index("ภูมิภาค")["ยอดขาย"]
    mom = ((cur - prev) / prev.replace(0, np.nan) * 100).fillna(0)

    # หา region ที่โตสูงสุด
    top_region = mom.sort_values(ascending=False).index[0]

    # Line chart ทั้งช่วงเวลา (เส้นของ top_region หนา + ไฮไลต์)
    fig = go.Figure()
    palette = {
        "ภาคเหนือ": "#636EFA", "ภาคตะวันออกเฉียงเหนือ": "#EF553B", "ภาคกลาง": "#00CC96",
        "ภาคตะวันออก": "#AB63FA", "ภาคตะวันตก": "#FFA15A", "ภาคใต้": "#19D3F3",
    }
    for region in reg["ภูมิภาค"].unique():
        y = reg[reg["ภูมิภาค"] == region]["ยอดขาย"].values
        line_w = 4 if region == top_region else 2
        marker_s = 8 if region == top_region else 5
        fig.add_trace(go.Scatter(
            x=month_cols, y=y, mode="lines+markers", name=region,
            line=dict(width=line_w, color=palette.get(region)),
            marker=dict(size=marker_s)
        ))

    # Annotation ชี้ region แชมป์ที่ปลายเส้น
    y_last = reg[(reg["ภูมิภาค"] == top_region) & (reg["เดือน"] == month_now)]["ยอดขาย"].values[0]
    fig.add_annotation(
        x=month_now, y=y_last, text=f"แชมป์ MoM: {top_region} (+{mom[top_region]:.2f}%)",
        showarrow=True, arrowhead=2, ax=30, ay=-40, bgcolor="rgba(255,255,255,.9)",
        bordercolor="#111", borderwidth=1
    )

    fig.update_layout(
        template=plotly_template, margin=dict(l=10, r=10, t=40, b=10),
        yaxis_title="ยอดขาย (บาท)", xaxis_title="เดือน",
        legend_title_text="", height=420,
        title=dict(text="แนวโน้มยอดขายรายภูมิภาค & ไฮไลต์ผู้ชนะรายเดือน", font=dict(size=20)),
        xaxis=dict(tickangle=-30, tickfont=dict(size=12)),
        yaxis=dict(tickfont=dict(size=12)),
        legend=dict(font=dict(size=12))
    )
    fig.update_traces(hovertemplate="%{x}<br>%{y:,.0f} บาท")
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False}, key=f"regional_growth_{key_prefix}")

def render_product_category_performance(df3, selected_month, plotly_template="plotly_white", key_prefix="prodcat"):
    st.subheader("Top ประเภทสินค้า OTOP ขายดี (รายเดือน)")
    # หาเดือนใน df3
    month_key = selected_month.split(" ")[0]
    idx_match = next((idx for idx in df3.index if str(idx).startswith(month_key)), None)
    if idx_match is None:
        st.info("ไม่พบข้อมูลประเภทสินค้าสำหรับเดือนนี้", icon="ℹ️")
        return
    s = df3.loc[idx_match].sort_values(ascending=True)  # สำหรับแสดงแนวนอน
    top_name = s.idxmax()
    top_val = s.max()

    # ใช้ go.Bar เพื่อไฮไลต์แท่งบนสุด
    colors = ["#D1D5DB"] * len(s)  # เทาอ่อนเป็นค่า default
    top_idx = list(s.index).index(top_name)
    colors[top_idx] = "#2563EB"     # ไฮไลต์น้ำเงินเข้ม

    fig = go.Figure(go.Bar(
        x=s.values, y=s.index, orientation="h",
        marker=dict(color=colors),
        text=[f"{v:,.0f}" for v in s.values],
        textposition="outside",
    ))

    fig.update_layout(
        template=plotly_template, margin=dict(l=10, r=10, t=40, b=10),
        xaxis_title="ยอดขาย (บาท)", yaxis_title="",
        height=420,
        title=dict(text=f"สัดส่วนยอดขายตามประเภทสินค้า — {selected_month}", font=dict(size=20)),
        xaxis=dict(tickfont=dict(size=12)), yaxis=dict(tickfont=dict(size=12)),
    )
    # Annotation ชี้หมวดแชมป์
    fig.add_annotation(
        x=top_val, y=top_name, text=f"แชมป์: {top_name} (฿{top_val:,.0f})",
        showarrow=True, arrowhead=2, ax=40, ay=-10,
        bgcolor="rgba(255,255,255,.9)", bordercolor="#111", borderwidth=1
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False}, key=f"prodcat_{key_prefix}")
