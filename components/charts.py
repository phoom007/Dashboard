# components/charts.py
# -*- coding: utf-8 -*-
import streamlit as st
import plotly.express as px
import pandas as pd

# ====== ปุ่ม Pill สองชุด (ช่วงเวลา / ชนิดกราฟ) ======
def _render_pill_controls(default_range="ALL", default_kind="Stacked"):
    # เก็บสถานะไว้ใน session_state
    if "time_range" not in st.session_state:
        st.session_state.time_range = default_range
    if "bar_kind" not in st.session_state:
        st.session_state.bar_kind = default_kind

    colA, colB = st.columns([1,1])
    with colA:
        st.markdown('<div class="subtle">ช่วงเวลา</div>', unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            if st.button("ALL", key="pill_all"):
                st.session_state.time_range = "ALL"
        with c2:
            if st.button("1M", key="pill_1m"):
                st.session_state.time_range = "1M"
        with c3:
            if st.button("6M", key="pill_6m"):
                st.session_state.time_range = "6M"
        with c4:
            if st.button("1Y", key="pill_1y"):
                st.session_state.time_range = "1Y"

        # ทำให้ปุ่ม active ด้วย class
        st.markdown(
            f"""
<script>
const map = {{"ALL":"pill_all","1M":"pill_1m","6M":"pill_6m","1Y":"pill_1y"}};
Object.values(map).forEach(id => {{
  const el = window.parent.document.querySelector('button[kind="secondary"]#'+id) || 
             window.parent.document.querySelector('button[aria-label="'+id+'"]');
}});
</script>
            """,
            unsafe_allow_html=True,
        )

    with colB:
        st.markdown('<div class="subtle">ชนิดกราฟ</div>', unsafe_allow_html=True)
        d1, d2 = st.columns(2)
        with d1:
            if st.button("Stacked", key="pill_stacked"):
                st.session_state.bar_kind = "Stacked"
        with d2:
            if st.button("Clustered", key="pill_clustered"):
                st.session_state.bar_kind = "Clustered"

    # ใช้ CSS class แทน: เพิ่มคลาส is-active ให้ปุ่มที่เลือก
    st.markdown(
        f"""
<script>
(function(){{
  const doc = window.parent.document;

  function mark(id, active){{
    const btn = doc.querySelector('button#'+id) || doc.querySelector('button[aria-label="'+id+'"]');
    if(!btn) return;
    btn.classList.toggle('pill', true);
    btn.classList.toggle('is-active', active);
  }}

  const range = "{st.session_state.time_range}";
  mark("pill_all",  range==="ALL");
  mark("pill_1m",   range==="1M");
  mark("pill_6m",   range==="6M");
  mark("pill_1y",   range==="1Y");

  const kind = "{st.session_state.bar_kind}";
  mark("pill_stacked",   kind==="Stacked");
  mark("pill_clustered", kind==="Clustered");
}})();
</script>
        """,
        unsafe_allow_html=True,
    )

def render_main_row_charts(df1, df2, selected_month, plotly_template="plotly_white"):
    # กราฟเสาหลัก: โครงสร้างช่องทางตลอดช่วงเวลา (ใช้ df2 ทั้งตาราง)
    data = df2.reset_index().rename(columns={"index":"เดือน"})
    # ปรับช่วงเวลาแบบง่าย ๆ จากปุ่ม
    tail_map = {"ALL": len(data), "1M": 1, "6M": 6, "1Y": 12}
    n_tail = tail_map.get(st.session_state.get("time_range","ALL"), len(data))
    data = data.tail(n_tail)

    st.markdown('<div class="section-title">โครงสร้างช่องทาง</div>', unsafe_allow_html=True)
    _render_pill_controls()

    # เตรียมกว้าง->ยาว
    long_df = data.melt(id_vars="เดือน", var_name="ช่องทาง", value_name="value")
    barmode = "stack" if st.session_state.get("bar_kind","Stacked") == "Stacked" else "group"

    fig = px.bar(
        long_df, x="เดือน", y="value", color="ช่องทาง", barmode=barmode,
        template=plotly_template, labels={"value":"บาท (฿)"}
    )
    fig.update_layout(legend_title_text="", margin=dict(l=0,r=0,b=0,t=10))
    fig.update_traces(texttemplate="%{y:,.0f}", textposition="outside", cliponaxis=False)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

# ====== Revenue Sources (เดือนเดียว) ======
def render_revenue_sources(df2, selected_month, plotly_template="plotly_white"):
    st.markdown('<div class="section-title">Revenue Sources (เดือนเดียว)</div>', unsafe_allow_html=True)
    # หา row ของเดือนเดียว
    month_key = selected_month.split(" ")[0]  # "กันยายน"
    idx_match = next((idx for idx in df2.index if str(idx).startswith(month_key)), None)

    if idx_match is None:
        st.info("ไม่พบข้อมูลสำหรับเดือนที่เลือก")
        return

    s = df2.loc[idx_match]
    fig = px.pie(values=s.values, names=s.index, hole=.45, template=plotly_template)
    fig.update_layout(margin=dict(l=0,r=0,b=0,t=0), legend_title_text="")
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

# ====== แหล่งข้อมูลที่ใช้สร้าง Dashboard (ฝัง CDD) ======
def render_cdd_sources_embeds():
    st.markdown('<div class="section-title">แหล่งข้อมูลที่ใช้สร้าง Dashboard (ฝังจาก CDD)</div>', unsafe_allow_html=True)
    st.caption("ลิงก์อ้างอิง: otop_r06, otop_r05, otop_r04 — เปิดเป็น iframe เพื่อดูหน้าเว็บจริง")

    urls = [
        "https://logi.cdd.go.th/otop/cdd_report/otop_r06.php?year=2567",
        "https://logi.cdd.go.th/otop/cdd_report/otop_r05.php?year=2567",
        "https://logi.cdd.go.th/otop/cdd_report/otop_r04.php?year=2567&org_group=0",
    ]
    c1, c2, c3 = st.columns(3)
    with c1:
        st.components.v1.iframe(urls[0], height=360)
    with c2:
        st.components.v1.iframe(urls[1], height=360)
    with c3:
        st.components.v1.iframe(urls[2], height=360)

# ====== (ของเดิม) สรุปเชิงลึก + reuse ======
def render_transactions_and_sources(
    df1, df2, df3, selected_month, selected_province,
    channel_filter, product_filter, national_avg, plotly_template="plotly_white"
):
    # … (คุณคงมีคอนเทนต์เดิมของหน้า “วิเคราะห์เชิงลึก”) …
    # ต่อท้ายด้วย 2 ส่วนที่ต้องการให้มีในทุกแท็บ
    st.markdown("---")
    render_revenue_sources(df2, selected_month, plotly_template)
    st.markdown("---")
    render_cdd_sources_embeds()
