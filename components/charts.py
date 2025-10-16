# components/charts.py
# -*- coding: utf-8 -*-
from __future__ import annotations
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


# ------------------------------------------------------------
# 1) Revenue Sources (เดือนเดียว) — ปรับตามเดือน & แสดงบริบทจังหวัด
# ------------------------------------------------------------
def render_revenue_sources(
    df2: pd.DataFrame,
    selected_month: str,
    selected_province: str,
    plotly_template: str = "plotly_white",
    key_prefix: str = "revsrc",
) -> None:
    """
    แสดงสัดส่วนยอดขายตามช่องทาง (พายกราฟ) สำหรับ 'เดือนเดียว'
    - ข้อมูลช่องทางอิง df2 ซึ่งเป็นภาพรวมระดับประเทศ
    - จังหวัดที่เลือก ใช้แสดงในหัวเรื่องเพื่อให้ผู้อ่านรับรู้บริบท
    """
    st.markdown("### วงกลมสัดส่วนช่องทาง (Revenue Sources — เดือนเดียว)")

    if df2 is None or df2.empty:
        st.info("ไม่พบข้อมูลช่องทาง")
        return

    if selected_month not in df2.index:
        st.info("ไม่พบข้อมูลช่องทางสำหรับเดือนที่เลือก")
        return

    series = df2.loc[selected_month]
    df_plot = series.reset_index()
    df_plot.columns = ["ช่องทาง", "ยอดขาย"]

    fig = px.pie(
        df_plot,
        values="ยอดขาย",
        names="ช่องทาง",
        hole=0.40,
        template=plotly_template,
    )
    fig.update_traces(
        textposition="inside",
        textinfo="percent+label",
        pull=[0.03, 0, 0, 0],
    )
    fig.update_layout(
        title=dict(
            text=f"สัดส่วนยอดขายตามช่องทาง — {selected_month} — จังหวัดที่เลือก: {selected_province}",
            x=0.5,
            xanchor="center",
            font=dict(size=18),
        ),
        showlegend=False,
        margin=dict(t=60, r=10, b=10, l=10),
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"displayModeBar": False},
        key=f"plot_revsrc_{key_prefix}_{selected_month}_{selected_province}",
    )
    st.caption(
        "※ หมายเหตุ: ข้อมูลช่องทางเป็นภาพรวมระดับประเทศ (อ้างอิง df2) — ปรับตามเดือนจริง, ส่วนจังหวัดใช้เพื่อบริบทการอ่าน"
    )


# ------------------------------------------------------------
# 2) Main row charts (เวอร์ชันเบาๆ กัน ImportError ระหว่างโปรเจกต์)
#    - ถ้าโปรเจกต์เดิมมีเวอร์ชันสมบูรณ์อยู่แล้ว จะไม่กระทบ
# ------------------------------------------------------------
def render_main_row_charts(
    df1: pd.DataFrame,
    df2: pd.DataFrame,
    selected_month: str,
    month_cols: list[str] | None = None,
    selected_province: str | None = None,
    plotly_template: str = "plotly_white",
    key_prefix: str = "main",
) -> None:
    """
    กราฟหลักแถวแรก (ตัวอย่าง minimal) — ถ้ามีเวอร์ชันเต็มในโปรเจกต์เดิม
    ให้ใช้ของเดิมได้เลย ฟังก์ชันนี้จะไม่รบกวน
    """
    if (df1 is None) or df1.empty:
        return

    # กราฟเส้นแนวโน้มเฉลี่ยประเทศ (minimal)
    if month_cols is None:
        month_cols = [c for c in df1.columns if ("2566" in c or "2567" in c)]
    if not month_cols:
        return

    nat_avg = df1[month_cols].mean()
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=month_cols,
        y=nat_avg.values,
        mode="lines+markers",
        name="เฉลี่ยประเทศ",
    ))
    fig.update_layout(
        template=plotly_template,
        title=dict(text="แนวโน้มยอดขายเฉลี่ยทั้งประเทศ (ตัวอย่างย่อ)", x=0.5, font=dict(size=18)),
        margin=dict(t=60, r=10, b=10, l=10),
        height=320,
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False}, key=f"plot_mainrow_{key_prefix}")


# ------------------------------------------------------------
# 3) ฝังหน้าเว็บแหล่งข้อมูล CDD (แสดงได้ทั้ง 2 แท็บ)
# ------------------------------------------------------------
def render_cdd_sources_embeds(key_prefix: str = "tab") -> None:
    """
    ฝัง 3 หน้า CDD ที่เป็นต้นทางข้อมูล เพื่อโปร่งใส/อ้างอิง
    """
    url_map = {
        "r06": "https://logi.cdd.go.th/otop/cdd_report/otop_r06.php?year=2567",
        "r05": "https://logi.cdd.go.th/otop/cdd_report/otop_r05.php?year=2567",
        "r04": "https://logi.cdd.go.th/otop/cdd_report/otop_r04.php?year=2567&org_group=0",
    }
    st.markdown("### แหล่งข้อมูลที่ใช้สร้าง Dashboard (ฝังจาก CDD)")
    for code, url in url_map.items():
        st.markdown(f"**{code.upper()}**")
        # streamlit cloud ไม่รองรับ key ใน iframe -> ไม่ส่ง key
        st.components.v1.iframe(url, height=420, scrolling=True)
        st.markdown("---")
