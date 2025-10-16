# components/charts.py (แทนที่บล็อกฟังก์ชันทั้งไฟล์เดิมได้เลย)
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.formatters import fmt_baht
import random

def render_main_row_charts(df1, df2, selected_month, plotly_template="plotly_white"):
    colL, colR = st.columns([3,2])

    # ----- Left: Revenue Trend (ALL/1M/6M/1Y)
    with colL:
        st.subheader("แนวโน้มรายได้ (Revenue)")
        timewin = st.radio("ช่วงเวลา", options=["ALL","1M","6M","1Y"], index=0, horizontal=True)
        series = df1.sum(axis=0)  # รวมทุกจังหวัดรายเดือน
        months = series.index.tolist()

        def subset(win):
            if win == "ALL":
                return months, series.values
            if win == "1M":
                return [months[-1]], [series.iloc[-1]]
            if win == "6M":
                return months[-6:], series.iloc[-6:].values
            if win == "1Y":
                return months[-12:], series.iloc[-12:].values

        x, y = subset(timewin)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x, y=y, mode="lines+markers", name="ยอดขายรวม"))
        fig.update_layout(template=plotly_template, height=380,
                          xaxis_title="เดือน", yaxis_title="ยอดขาย (บาท)")
        st.plotly_chart(fig, use_container_width=True)
        st.caption("คำอธิบาย: เส้นนี้แสดงแนวโน้มยอดขายรวมของทั้งประเทศตามช่วงเวลาที่เลือก (ALL/1M/6M/1Y)")

    # ----- Right: Channel Structure (toggle)
    with colR:
        st.subheader("โครงสร้างช่องทาง")
        chart_mode = st.radio("ชนิดกราฟ", options=["Stacked","Clustered"], index=0, horizontal=True)
        df2_plot = df2.reset_index().rename(columns={"index":"เดือน"})
        fig2 = px.bar(df2_plot, x="เดือน", y=df2.columns, template=plotly_template)
        fig2.update_layout(barmode="stack" if chart_mode=="Stacked" else "group",
                           height=380, legend_title="ช่องทาง")
        fig2.update_xaxes(tickangle=-45)
        st.plotly_chart(fig2, use_container_width=True)
        st.caption("คำอธิบาย: แท่งแสดงมูลค่าตามช่องทางขายในแต่ละเดือน จะซ้อนหรือวางคู่กันได้จากสวิตช์ด้านบน")

def _fake_transactions(df1, df2, df3, selected_month, n=12):
    provinces = df1.index.tolist()
    channels = df2.columns.tolist()
    cats = df3.columns.tolist()

    records = []
    for _ in range(n):
        p = random.choice(provinces)
        c = random.choice(channels)
        k = random.choice(cats)
        amt = abs(float(df1.loc[p, selected_month])) * random.uniform(0.001, 0.01)
        day = random.randint(1, 28)
        # ใช้สตริง timestamp แบบง่ายเพื่อกัน parse พัง
        ts = f"{day:02d} {selected_month}, 10:{random.randint(10,59):02d} น."
        status = random.choices(["Success","Cancelled","Pending"], weights=[0.75,0.1,0.15])[0]
        records.append({
            "Name": random.choice(["Adam M","Alexa Newsome","Shelly Dorey","Anucha P.","Kanya T."]),
            "Description": f"ยอดขายจังหวัด {p} – ช่องทาง {c} – ประเภท {k}",
            "Channel": c,
            "Province": p,
            "Category": k,
            "Amount (฿)": fmt_baht(amt, no_prefix=True),
            "Timestamp": ts,
            "Status": status
        })
    return pd.DataFrame(records)

def render_transactions_and_sources(df1, df2, df3, selected_month, selected_province,
                                    channel_filter, product_filter, national_avg,
                                    plotly_template="plotly_white"):
    # แนวโน้มจังหวัด vs ค่าเฉลี่ยประเทศ
    st.subheader(f"แนวโน้มยอดขาย: {selected_province if selected_province!='ภาพรวม' else 'ภาพรวม'} เทียบค่าเฉลี่ยประเทศ")
    fig = go.Figure()
    if selected_province != "ภาพรวม":
        fig.add_trace(go.Scatter(x=df1.columns, y=df1.loc[selected_province], mode="lines+markers", name=selected_province))
    fig.add_trace(go.Scatter(x=df1.columns, y=national_avg, mode="lines", name="ค่าเฉลี่ยประเทศ", line=dict(dash="dash")))
    fig.update_layout(template=plotly_template, height=380, xaxis_title="เดือน", yaxis_title="ยอดขาย (บาท)",
                      legend=dict(y=0.95, x=0.01))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    col1, col2 = st.columns([1.2,1])
    with col1:
        st.markdown("#### Transactions (ตัวอย่างจำลอง)")
        st.dataframe(_fake_transactions(df1, df2, df3, selected_month), use_container_width=True, height=420)
    with col2:
        st.markdown("#### Revenue Sources (เดือนเดียว)")
        month_key = selected_month.split(' ')[0]
        idx_match = next((idx for idx in df2.index if str(idx).startswith(month_key)), None)
        if idx_match:
            vals = df2.loc[idx_match]
            fig_pie = px.pie(values=vals.values, names=vals.index, hole=.45, template=plotly_template)
            fig_pie.update_layout(height=420)
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("ไม่พบข้อมูลช่องทางของเดือนนี้")
