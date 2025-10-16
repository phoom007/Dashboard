# components/charts.py
# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from typing import List
from plotly.subplots import make_subplots

# ------------------------------
# Controls (ช่วงเวลา / ชนิดกราฟ)
# ------------------------------
def _unique_suffix(prefix: str) -> str:
    if "_ctrl_counts" not in st.session_state:
        st.session_state._ctrl_counts = {}
    cnt = st.session_state._ctrl_counts.get(prefix, 0) + 1
    st.session_state._ctrl_counts[prefix] = cnt
    return f"{prefix}_{cnt}"

def render_time_kind_controls(prefix="main"):
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
# กราฟหลักแถวแรก (ปรับตามจังหวัด)
# ------------------------------
def render_main_row_charts(
    df1,
    df2,
    selected_month,
    month_cols: List[str],
    selected_province: str,
    plotly_template="plotly_white",
    key_prefix="main",
):
    tail_map = {"ALL": len(df2), "1M": 1, "6M": 6, "1Y": 12}
    n_tail = tail_map.get(st.session_state.get("time_range", "ALL"), len(df2))
    barmode = "stack" if st.session_state.get("bar_kind", "Stacked") == "Stacked" else "group"

    # เตรียมข้อมูลกราฟแท่ง (ช่องทางระดับประเทศ)
    d2 = df2.reset_index().tail(n_tail)
    long_df = d2.melt(id_vars="เดือน", var_name="ช่องทาง", value_name="value")
    channels = long_df["ช่องทาง"].unique().tolist()
    months_tail = d2["เดือน"].tolist()

    left, right = st.columns([3, 2], gap="large")

    # ---------- ซ้าย: ช่องทาง + เส้นจังหวัด ----------
    with left:
        st.subheader("โครงสร้างช่องทางตามช่วงเวลา")
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        # Bars ต่อช่องทาง
        for ch in channels:
            df_ch = long_df[long_df["ช่องทาง"] == ch]
            fig.add_trace(
                go.Bar(
                    x=df_ch["เดือน"],
                    y=df_ch["value"],
                    name=ch,
                    text=[f"{v:,.0f}" for v in df_ch["value"]],
                    textposition="outside",
                ),
                secondary_y=False,
            )
        # เส้นจังหวัด (secondary axis)
        if selected_province and selected_province != "ภาพรวม" and selected_province in df1.index:
            ser = df1.loc[selected_province, month_cols]
            # ตัดให้เหลือช่วงเดียวกับแท่ง
            ser = ser[ser.index.isin(months_tail)]
            fig.add_trace(
                go.Scatter(
                    x=ser.index.tolist(),
                    y=ser.values.tolist(),
                    mode="lines+markers",
                    name=f"แนวโน้มจังหวัด: {selected_province}",
                    line=dict(width=4, color="#111827"),
                    marker=dict(size=8),
                    hovertemplate="%{x}<br>%{y:,.0f} บาท",
                ),
                secondary_y=True,
            )
        fig.update_layout(
            barmode="stack" if barmode == "stack" else "group",
            template=plotly_template,
            margin=dict(l=0, r=0, b=0, t=10),
            legend_title_text="",
            xaxis=dict(tickangle=-30),
        )
        fig.update_yaxes(title_text="บาท (฿) — ช่องทางระดับประเทศ", secondary_y=False)
        fig.update_yaxes(title_text="บาท (฿) — จังหวัดที่เลือก", secondary_y=True)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False}, key=f"main_mix_{key_prefix}")

    # ---------- ขวา: Top 20 จังหวัดของเดือน ----------
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
# Regional Growth Trend & Product Category Charts
# ======================================================

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

def _region_of_province(province: str) -> str:
    for r, provs in _REGION_MAP.items():
        if province in provs:
            return r
    return ""

def render_regional_growth(
    df1,
    month_cols: List[str],
    selected_month: str,
    selected_province: str = "ภาพรวม",
    plotly_template="plotly_white",
    key_prefix="regional",
):
    st.subheader("การเติบโตยอดขายตามภูมิภาค (Regional Growth)")
    reg = _build_regional_df(df1, month_cols)
    if reg.empty:
        st.info("ไม่มีข้อมูลภูมิภาคเพียงพอ", icon="ℹ️")
        return

    # เดือนปัจจุบัน/ก่อนหน้า
    try:
        m_idx = month_cols.index(selected_month)
    except ValueError:
        m_idx = len(month_cols) - 1
    prev_idx = max(0, m_idx - 1)
    month_now, month_prev = month_cols[m_idx], month_cols[prev_idx]

    cur = reg[reg["เดือน"] == month_now].set_index("ภูมิภาค")["ยอดขาย"]
    prev = reg[reg["เดือน"] == month_prev].set_index("ภูมิภาค")["ยอดขาย"]
    mom = ((cur - prev) / prev.replace(0, np.nan) * 100).fillna(0)

    # ผู้ชนะ MoM
    top_region = mom.sort_values(ascending=False).index[0]
    # ภูมิภาคของจังหวัดที่เลือก
    sel_region = _region_of_province(selected_province) if selected_province and selected_province != "ภาพรวม" else ""

    fig = go.Figure()
    palette = {
        "ภาคเหนือ": "#636EFA", "ภาคตะวันออกเฉียงเหนือ": "#EF553B", "ภาคกลาง": "#00CC96",
        "ภาคตะวันออก": "#AB63FA", "ภาคตะวันตก": "#FFA15A", "ภาคใต้": "#19D3F3",
    }
    for region in reg["ภูมิภาค"].unique():
        y = reg[reg["ภูมิภาค"] == region]["ยอดขาย"].values
        # เน้นเส้น: ชนะ MoM = หนา / ภูมิภาคของจังหวัดที่เลือก = หนาที่สุด
        if sel_region and region == sel_region:
            line_w, marker_s, line_color = 5, 9, "#111827"
        elif region == top_region:
            line_w, marker_s, line_color = 4, 8, palette.get(region)
        else:
            line_w, marker_s, line_color = 2, 5, palette.get(region)
        fig.add_trace(go.Scatter(
            x=month_cols, y=y, mode="lines+markers", name=region,
            line=dict(width=line_w, color=line_color),
            marker=dict(size=marker_s)
        ))

    # Annotation
    y_top = reg[(reg["ภูมิภาค"] == top_region) & (reg["เดือน"] == month_now)]["ยอดขาย"].values[0]
    fig.add_annotation(
        x=month_now, y=y_top, text=f"แชมป์ MoM: {top_region} (+{mom[top_region]:.2f}%)",
        showarrow=True, arrowhead=2, ax=30, ay=-40, bgcolor="rgba(255,255,255,.9)",
        bordercolor="#111", borderwidth=1
    )
    if sel_region:
        y_sel = reg[(reg["ภูมิภาค"] == sel_region) & (reg["เดือน"] == month_now)]["ยอดขาย"].values[0]
        fig.add_annotation(
            x=month_now, y=y_sel, text=f"จังหวัดที่เลือกอยู่ใน: {sel_region}",
            showarrow=True, arrowhead=2, ax=-40, ay=-10, bgcolor="rgba(255,255,255,.9)",
            bordercolor="#111", borderwidth=1
        )

    fig.update_layout(
        template=plotly_template, margin=dict(l=10, r=10, t=40, b=10),
        yaxis_title="ยอดขาย (บาท)", xaxis_title="เดือน",
        legend_title_text="", height=420,
        title=dict(text="แนวโน้มยอดขายรายภูมิภาค (ไฮไลต์จังหวัดที่เลือก)", font=dict(size=20)),
        xaxis=dict(tickangle=-30, tickfont=dict(size=12)),
        yaxis=dict(tickfont=dict(size=12)),
        legend=dict(font=dict(size=12))
    )
    fig.update_traces(hovertemplate="%{x}<br>%{y:,.0f} บาท")
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False}, key=f"regional_{key_prefix}")

def render_product_category_performance(
    df3,
    selected_month: str,
    selected_province: str = "ภาพรวม",
    plotly_template="plotly_white",
    key_prefix="prodcat",
):
    # แจ้งว่าข้อมูลหมวดสินค้าระดับจังหวัดยังไม่มี
    title_suffix = f" — {selected_month}"
    if selected_province and selected_province != "ภาพรวม":
        st.info(f"ยังไม่มีข้อมูลสัดส่วนหมวดสินค้าแยกตามจังหวัด • แสดงภาพรวมทั้งประเทศแทน ({selected_month})", icon="ℹ️")
        title_suffix = f" — {selected_month} (ภาพรวมประเทศ)"

    # หาเดือนใน df3
    month_key = selected_month.split(" ")[0]
    idx_match = next((idx for idx in df3.index if str(idx).startswith(month_key)), None)
    if idx_match is None:
        st.info("ไม่พบข้อมูลประเภทสินค้าสำหรับเดือนนี้", icon="ℹ️")
        return
    s = df3.loc[idx_match].sort_values(ascending=True)
    top_name = s.idxmax()
    top_val = s.max()

    colors = ["#D1D5DB"] * len(s)
    colors[list(s.index).index(top_name)] = "#2563EB"

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
        title=dict(text=f"Top ประเภทสินค้า OTOP ขายดี{title_suffix}", font=dict(size=20)),
        xaxis=dict(tickfont=dict(size=12)), yaxis=dict(tickfont=dict(size=12)),
    )
    fig.add_annotation(
        x=top_val, y=top_name, text=f"แชมป์: {top_name} (฿{top_val:,.0f})",
        showarrow=True, arrowhead=2, ax=40, ay=-10,
        bgcolor="rgba(255,255,255,.9)", bordercolor="#111", borderwidth=1
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False}, key=f"prodcat_{key_prefix}")
