# components/charts.py
# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import List

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


# ---------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------
def _find_month_index_like(df_index: pd.Index, selected_month: str) -> str | None:
    """หา index ของเดือนใน df2/df3 ที่มีรูปแบบ 'กันยายน 2567'
    จากค่า selected_month ที่มาจากคอลัมน์ของ df1 (มักจะ 'กันยายน 2567' เช่นกัน)
    ใช้ startswith เดือนไทยกันเคส spacing เล็กน้อย
    """
    if selected_month in df_index:
        return selected_month
    month_key = str(selected_month).split(" ")[0]
    for idx in df_index:
        if str(idx).startswith(month_key):
            return idx
    return None


# ---------------------------------------------------------------------
# 1) แถวกราฟหลัก (ซ้าย=แนวโน้มรายได้, ขวา=โครงสร้างช่องทางตามเวลา)
# ---------------------------------------------------------------------
def render_main_row_charts(
    df1: pd.DataFrame,
    df2: pd.DataFrame,
    selected_month: str,
    month_cols: List[str],
    selected_province: str,
    plotly_template: str = "plotly_white",
    key_prefix: str = "main",
) -> None:
    """แสดงกราฟหลักสองฝั่ง
    - ฝั่งซ้าย: แนวโน้มรายได้ (รวมประเทศ + จังหวัดที่เลือก)
    - ฝั่งขวา: โครงสร้างช่องทางตามช่วงเวลา (Stacked/Clustered)
    """
    col_l, col_r = st.columns(2)

    # --- ฝั่งซ้าย: แนวโน้มรายได้ ---
    with col_l:
        st.subheader("แนวโน้มรายได้ (Revenue)")
        # รวมประเทศรายเดือน
        national_total = df1[month_cols].sum()

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=month_cols,
                y=national_total.values,
                name="รวมประเทศ",
                mode="lines+markers",
                line=dict(width=3),
            )
        )
        if selected_province and selected_province != "ภาพรวม" and selected_province in df1.index:
            fig.add_trace(
                go.Scatter(
                    x=month_cols,
                    y=df1.loc[selected_province, month_cols].values,
                    name=selected_province,
                    mode="lines+markers",
                    line=dict(width=3, dash="dash"),
                )
            )

        fig.update_layout(
            template=plotly_template,
            height=420,
            margin=dict(l=10, r=10, t=20, b=10),
            legend=dict(orientation="h", y=1.1),
            xaxis=dict(tickangle=-45, title="เดือน"),
            yaxis=dict(title="บาท"),
        )
        st.plotly_chart(fig, use_container_width=True, key=f"trend_{key_prefix}")

    # --- ฝั่งขวา: โครงสร้างช่องทางตามช่วงเวลา ---
    with col_r:
        st.subheader("โครงสร้างช่องทาง")
        # Melt df2 เพื่อนำไปทำ stacked/clustered bar
        df2_plot = df2.copy()
        df2_plot = df2_plot.reset_index().rename(columns={"index": "เดือน"})
        df2_long = df2_plot.melt(
            id_vars="เดือน",
            var_name="ช่องทาง",
            value_name="มูลค่า (บาท)",
        )
        fig2 = px.bar(
            df2_long,
            x="เดือน",
            y="มูลค่า (บาท)",
            color="ช่องทาง",
            barmode="stack",
            template=plotly_template,
            height=420,
        )
        fig2.update_layout(
            margin=dict(l=10, r=10, t=20, b=10),
            xaxis=dict(tickangle=-45),
            legend=dict(orientation="h", y=1.1),
        )
        st.plotly_chart(fig2, use_container_width=True, key=f"channels_time_{key_prefix}")


# ---------------------------------------------------------------------
# 2) Revenue Sources (พายรายเดือน) – อิงเดือน + (รับจังหวัดมาเผื่อ/ไม่มีผล)
# ---------------------------------------------------------------------
def render_revenue_sources(
    df2: pd.DataFrame,
    selected_month: str,
    selected_province: str | None = None,
    plotly_template: str = "plotly_white",
    key_prefix: str = "rs",
) -> None:
    """พาย 'สัดส่วนช่องทาง' สำหรับเดือนเดียว
    หมายเหตุ: df2 เป็นข้อมูลระดับประเทศ จึงไม่ได้ downscale ตามจังหวัด
    """
    st.subheader("Revenue Sources (เดือนเดียว)")
    month_idx = _find_month_index_like(df2.index, selected_month)
    if month_idx is None:
        st.info("ไม่พบข้อมูลเดือนที่เลือกในชุดช่องทาง")
        return

    row = df2.loc[month_idx]
    fig = px.pie(
        values=row.values,
        names=row.index,
        hole=0.45,
        template=plotly_template,
        title="",
        height=360,
    )
    fig.update_traces(textposition="outside", textinfo="percent+label")
    fig.update_layout(margin=dict(l=10, r=10, t=0, b=10))
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False}, key=f"pie_{key_prefix}_{month_idx}")


# ---------------------------------------------------------------------
# 3) CDD Sources (ฝังจากเว็บ CDD) – แสดงในทั้งสองแท็บ
# ---------------------------------------------------------------------
def render_cdd_sources_embeds(key_prefix: str = "tab") -> None:
    """ฝังหน้าเว็บที่เป็นแหล่งข้อมูลจาก CDD (สามหน้าหลัก)"""
    st.subheader("แหล่งข้อมูลที่ใช้สร้าง Dashboard (ฝังจาก CDD)")
    col1, col2, col3 = st.columns(3)
    urls = {
        "r06": "https://logi.cdd.go.th/otop/cdd_report/otop_r06.php?year=2567",
        "r05": "https://logi.cdd.go.th/otop/cdd_report/otop_r05.php?year=2567",
        "r04": "https://logi.cdd.go.th/otop/cdd_report/otop_r04.php?year=2567&org_group=0",
    }
    with col1:
        st.caption("otop_r06 (ช่องทาง/พื้นที่)")
        st.components.v1.iframe(urls["r06"], height=420, scrolling=True)
    with col2:
        st.caption("otop_r05 (ประเภทสินค้า)")
        st.components.v1.iframe(urls["r05"], height=420, scrolling=True)
    with col3:
        st.caption("otop_r04 (ภาพรวม)")
        st.components.v1.iframe(urls["r04"], height=420, scrolling=True)
