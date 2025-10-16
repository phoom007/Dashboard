# components/charts.py
# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


# ------------------------------------------------------------
# Revenue Sources (เดือนเดียว) — อิง df2 ระดับประเทศ
# แสดงจังหวัดเพื่อบริบท (ยังไม่กรองรายจังหวัด)
# ------------------------------------------------------------
def render_revenue_sources(df2, selected_month, selected_province, plotly_template="plotly_white", key_prefix="revsrc"):
    st.markdown("### วงกลมสัดส่วนช่องทาง (Revenue Sources — เดือนเดียว)")

    if df2 is None or len(df2) == 0:
        st.info("ไม่พบข้อมูลช่องทาง")
        return

    if selected_month not in df2.index:
        st.info("ไม่พบข้อมูลช่องทางสำหรับเดือนที่เลือก")
        return

    s = df2.loc[selected_month]
    df_plot = s.reset_index()
    df_plot.columns = ["ช่องทาง", "ยอดขาย"]

    fig = px.pie(
        df_plot,
        values="ยอดขาย",
        names="ช่องทาง",
        hole=0.4,
        template=plotly_template,
    )
    fig.update_traces(textposition="inside", textinfo="percent+label", pull=[0.03, 0, 0, 0])
    fig.update_layout(
        title=dict(
            text=f"สัดส่วนยอดขายตามช่องทาง — {selected_month} — จังหวัดที่เลือก: {selected_province}",
            x=0.5,
            font=dict(size=18),
        ),
        showlegend=False,
        margin=dict(t=60, r=10, b=10, l=10),
        height=380,
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"displayModeBar": False},
        key=f"plot_revsrc_{key_prefix}_{selected_month}_{selected_province}",
    )
    st.caption("หมายเหตุ: ข้อมูลช่องทางเป็นระดับประเทศ (อ้างอิง df2) — จังหวัดใช้เพื่อบริบทการอ่าน")


# ------------------------------------------------------------
# กราฟหลักแถวแรก (เวอร์ชันย่อเพื่อความเข้ากันได้)
# ------------------------------------------------------------
def render_main_row_charts(
    df1,
    df2,
    selected_month,
    month_cols=None,
    selected_province=None,
    plotly_template="plotly_white",
    key_prefix="main",
):
    if df1 is None or len(df1) == 0:
        return

    if month_cols is None:
        month_cols = [c for c in df1.columns if ("2566" in c or "2567" in c)]
    if not month_cols:
        return

    nat_avg = df1[month_cols].mean()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=month_cols, y=nat_avg.values, mode="lines+markers", name="เฉลี่ยประเทศ"))
    fig.update_layout(
        template=plotly_template,
        title=dict(text="แนวโน้มยอดขายเฉลี่ยทั้งประเทศ (ตัวอย่างย่อ)", x=0.5, font=dict(size=18)),
        margin=dict(t=60, r=10, b=10, l=10),
        height=320,
    )
    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"displayModeBar": False},
        key=f"plot_mainrow_{key_prefix}",
    )


# ------------------------------------------------------------
# ฝังหน้าเว็บแหล่งข้อมูล CDD (แสดงได้ทั้ง 2 แท็บ)
# ------------------------------------------------------------
def render_cdd_sources_embeds(key_prefix="tab"):
    st.markdown("### แหล่งข้อมูลที่ใช้สร้าง Dashboard (ฝังจาก CDD)")

    srcs = [
        ("R06", "https://logi.cdd.go.th/otop/cdd_report/otop_r06.php?year=2567"),
        ("R05", "https://logi.cdd.go.th/otop/cdd_report/otop_r05.php?year=2567"),
        ("R04", "https://logi.cdd.go.th/otop/cdd_report/otop_r04.php?year=2567&org_group=0"),
    ]
    for label, url in srcs:
        st.markdown(f"**{label}**")
        # Streamlit cloud ยังไม่รองรับ key ใน iframe -> ไม่ส่ง key
        st.components.v1.iframe(url, height=420, scrolling=True)
        st.markdown("---")
