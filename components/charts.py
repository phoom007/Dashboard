# components/charts.py  (เฉพาะฟังก์ชันนี้)
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.formatters import fmt_baht
import random
import streamlit.components.v1 as components

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

    # ====== โหมดการแสดง Transactions ======
    mode = st.radio("แสดง Transactions แบบ:", ["ฝังหน้าเว็บ CDD (แนะนำ)", "ข้อมูลจำลองในแดชบอร์ด"], horizontal=True, index=0)

    col1, col2 = st.columns([1.2,1])

    with col1:
        st.markdown("#### Transactions")
        if mode == "ฝังหน้าเว็บ CDD (แนะนำ)":
            st.caption("แหล่งที่มา: https://logi.cdd.go.th/otop/")
            try:
                # ฝังเว็บโดยตรง (ถ้าเว็บต้นทางอนุญาตให้ฝัง iframe)
                components.iframe("https://logi.cdd.go.th/otop/", height=900, scrolling=True)
                st.info("ถ้าไม่แสดง ให้กดปุ่มเปิดเว็บด้านล่าง (บางครั้งเว็บปลายทางปิดการฝัง)")
            except Exception as e:
                st.warning(f"ไม่สามารถฝังหน้าเว็บได้: {e}")
                st.link_button("เปิดหน้าเว็บ CDD", "https://logi.cdd.go.th/otop/")
        else:
            # ข้อมูลจำลอง (fallback/UI demo)
            st.caption("โหมดตัวอย่างจำลอง (Synthetic)")
            st.dataframe(_fake_transactions(df1, df2, df3, selected_month),
                         use_container_width=True, height=720)
            st.info("นี่เป็นข้อมูลตัวอย่างเพื่อสาธิต UI เท่านั้น — หากต้องการเชื่อมต่อข้อมูลจริง ต้องมี API/สิทธิ์จากระบบ CDD")

    with col2:
        st.markdown("#### Revenue Sources (เดือนเดียว)")
        month_key = selected_month.split(' ')[0]
        idx_match = next((idx for idx in df2.index if str(idx).startswith(month_key)), None)
        if idx_match:
            vals = df2.loc[idx_match]
            fig_pie = px.pie(values=vals.values, names=vals.index, hole=.45, template=plotly_template)
            fig_pie.update_layout(height=900)
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("ไม่พบข้อมูลช่องทางของเดือนนี้")
