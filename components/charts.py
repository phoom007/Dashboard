# components/charts.py
# -*- coding: utf-8 -*-
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components

# ---------------------- สีหลัก & utils ----------------------
ACCENT = "#2563eb"      # น้ำเงินเข้ม
ACCENT2 = "#f97316"     # ส้มใช้เน้น
GREY = "#6b7280"

def _fmt_baht(x: float) -> str:
    try:
        return f"฿{x:,.0f}"
    except Exception:
        return str(x)

def _apply_base_layout(fig, template="plotly_white", h=380):
    fig.update_layout(
        template=template,
        height=h,
        margin=dict(l=10, r=10, t=10, b=10),
        font=dict(size=13),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    )
    fig.update_xaxes(showgrid=True, gridcolor="rgba(0,0,0,0.06)", tickangle=-30)
    fig.update_yaxes(showgrid=True, gridcolor="rgba(0,0,0,0.06)")
    return fig


# ============================================================
#  กราฟหลักแถวแรก: (ซ้าย) แนวโน้มรายได้  (ขวา) โครงสร้างช่องทาง
# ============================================================
def render_main_row_charts(df1, df2, selected_month, plotly_template="plotly_white"):
    colL, colR = st.columns([3, 2])

    # ----- ซ้าย: Revenue Trend + Highlight เดือนที่เลือก -----
    with colL:
        st.subheader("แนวโน้มรายได้ (Revenue)")
        timewin = st.radio("ช่วงเวลา", options=["ALL", "1M", "6M", "1Y"], index=0, horizontal=True)

        series = df1.sum(axis=0)  # รวมทั้งประเทศรายเดือน
        months_all = list(series.index)

        def subset(win):
            if win == "ALL": return months_all, series.values
            if win == "1M":  return months_all[-1:], series.iloc[-1:].values
            if win == "6M":  return months_all[-6:], series.iloc[-6:].values
            if win == "1Y":  return months_all[-12:], series.iloc[-12:].values

        xs, ys = subset(timewin)

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=xs, y=ys, mode="lines+markers",
            name="ยอดขายรวม",
            line=dict(width=3, color=ACCENT),
            marker=dict(size=7)
        ))

        # MA3
        if len(ys) >= 3:
            ma = pd.Series(ys).rolling(3).mean()
            fig.add_trace(go.Scatter(
                x=xs, y=ma, mode="lines",
                name="ค่าเฉลี่ย 3 เดือน (MA3)",
                line=dict(width=2, dash="dot", color="#0ea5e9")
            ))

        # ไฮไลต์เดือนที่เลือก
        if selected_month in xs:
            sel_y = float(series[selected_month])
            fig.add_trace(go.Scatter(
                x=[selected_month], y=[sel_y],
                mode="markers",
                marker=dict(size=14, color=ACCENT2, line=dict(width=2, color="white")),
                name="เดือนที่เลือก",
                hovertemplate=f"{selected_month}<br>รวม {_fmt_baht(sel_y)}<extra></extra>"
            ))
            fig.add_annotation(
                x=selected_month, y=sel_y, text=_fmt_baht(sel_y),
                showarrow=True, arrowcolor=ACCENT2, arrowsize=1.2, arrowhead=2,
                bgcolor="rgba(255,255,255,.9)", bordercolor=ACCENT2, borderwidth=1,
                yshift=18
            )

        # เส้นค่าเฉลี่ยช่วงที่มองอยู่
        avg_val = float(pd.Series(ys).mean())
        fig.add_hline(
            y=avg_val,
            line=dict(color=GREY, width=1, dash="dash"),
            annotation_text=f"เฉลี่ย {_fmt_baht(avg_val)}",
            annotation_position="top left",
            annotation_font=dict(color=GREY)
        )

        _apply_base_layout(fig, plotly_template)
        fig.update_traces(hovertemplate="%{x}<br>รวม ฿%{y:,.0f}<extra></extra>")
        st.plotly_chart(fig, use_container_width=True)
        st.caption("เส้นสีน้ำเงิน = ยอดขายรวม; จุดส้ม = เดือนที่เลือก; เส้นประ = ค่าเฉลี่ยช่วงที่เปิดดู")

    # ----- ขวา: โครงสร้างช่องทาง (แก้เลขทับกัน) -----
    with colR:
        st.subheader("โครงสร้างช่องทาง")
        mode = st.radio("ชนิดกราฟ", options=["Stacked", "Clustered"], index=0, horizontal=True)

        dplot = df2.reset_index().rename(columns={"index": "เดือน"})
        months = dplot["เดือน"].tolist()
        fig2 = go.Figure()

        palette = ["#1d4ed8", "#60a5fa", "#10b981", "#f59e0b"]
        for i, col in enumerate(df2.columns):
            fig2.add_bar(
                x=months, y=dplot[col], name=col, marker_color=palette[i % len(palette)],
                hovertemplate="%{x}<br>%{fullData.name}: ฿%{y:,.0f}<extra></extra>"
            )

        totals = dplot[df2.columns].sum(axis=1).astype(float)

        # เลือกความถี่ข้อความรวมเพื่อกันทับ
        n = len(months)
        step = 1
        if n >= 10: step = 2
        if n >= 15: step = 3
        text_labels = [f"฿{v:,.0f}" if (i % step == 0) else "" for i, v in enumerate(totals)]

        fig2.add_trace(go.Scatter(
            x=months, y=totals,
            mode="lines+markers+text",
            line=dict(color="#111827", width=2),
            marker=dict(size=6, color="#111827"),
            text=text_labels, textposition="top center", textfont=dict(size=11),
            name="รวมต่อเดือน",
            hovertemplate="%{x}<br>รวม: ฿%{y:,.0f}<extra></extra>",
            cliponaxis=False
        ))

        ymax = float(totals.max()) * 1.15  # headroom กันชน
        fig2.update_yaxes(range=[0, ymax])

        fig2.update_layout(barmode="stack" if mode == "Stacked" else "group")
        _apply_base_layout(fig2, plotly_template)
        fig2.update_xaxes(tickangle=-30, tickfont=dict(size=11))
        st.plotly_chart(fig2, use_container_width=True)
        st.caption("สีแทนแต่ละช่องทาง; ตัวเลขด้านบน (เว้นช่วงอัตโนมัติ) คือยอดรวมต่อเดือน")


# =====================================================================
#  ส่วนลึก: แนวโน้มจังหวัด + แหล่งข้อมูล CDD + โดนัท Revenue Sources
# =====================================================================
def render_transactions_and_sources(
    df1, df2, df3, selected_month, selected_province,
    channel_filter, product_filter, national_avg,
    plotly_template="plotly_white",
):
    # แนวโน้มจังหวัดเทียบประเทศ
    st.subheader(f"แนวโน้มยอดขาย: {selected_province if selected_province!='ภาพรวม' else 'ภาพรวม'} เทียบค่าเฉลี่ยประเทศ")

    fig = go.Figure()
    if selected_province != "ภาพรวม":
        y_prov = df1.loc[selected_province]
        fig.add_trace(go.Scatter(
            x=df1.columns, y=y_prov,
            mode="lines+markers", name=selected_province,
            line=dict(color=ACCENT, width=3), marker=dict(size=7)
        ))
        if selected_month in df1.columns:
            sel_y = float(y_prov[selected_month])
            fig.add_trace(go.Scatter(
                x=[selected_month], y=[sel_y],
                mode="markers", marker=dict(size=14, color=ACCENT2, line=dict(width=2, color="white")),
                name="เดือนที่เลือก (จังหวัด)"
            ))

    fig.add_trace(go.Scatter(
        x=df1.columns, y=national_avg,
        mode="lines", name="ค่าเฉลี่ยประเทศ",
        line=dict(dash="dash", width=2, color="#111827")
    ))

    _apply_base_layout(fig, plotly_template)
    fig.update_traces(hovertemplate="%{x}<br>฿%{y:,.0f}<extra></extra>")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    colLeft, colRight = st.columns([1.25, 1])

    # ===== ซ้าย: แหล่งข้อมูลที่ใช้สร้าง Dashboard (ฝัง r06/r05/r04) =====
    with colLeft:
        st.markdown("#### แหล่งข้อมูลที่ใช้สร้าง Dashboard (ฝังจาก CDD)")

        # ปี พ.ศ. จากเดือนที่เลือก (เช่น 'กันยายน 2567'); ถ้า parse ไม่ได้ ให้ 2567
        try:
            th_year = int(str(selected_month).split()[-1])
        except Exception:
            th_year = 2567

        url_r06 = f"https://logi.cdd.go.th/otop/cdd_report/otop_r06.php?year={th_year}"
        url_r05 = f"https://logi.cdd.go.th/otop/cdd_report/otop_r05.php?year={th_year}"
        url_r04 = f"https://logi.cdd.go.th/otop/cdd_report/otop_r04.php?year={th_year}&org_group=0"

        st.caption("3 รายงานต้นทางที่ใช้ประกอบคำนวณในแดชบอร์ดชุดนี้ (r06: ช่องทาง, r05: ประเภทสินค้า, r04: รายจังหวัด)")
        t1, t2, t3 = st.tabs([f"r06 (ช่องทาง) • {th_year}", f"r05 (ประเภทสินค้า) • {th_year}", f"r04 (รายจังหวัด) • {th_year}"])

        with t1:
            try:
                components.iframe(url_r06, height=900, scrolling=True)
            except Exception:
                st.warning("ไม่สามารถฝังหน้า r06 ได้")
            st.link_button("เปิด r06 ในแท็บใหม่", url_r06)

        with t2:
            try:
                components.iframe(url_r05, height=900, scrolling=True)
            except Exception:
                st.warning("ไม่สามารถฝังหน้า r05 ได้")
            st.link_button("เปิด r05 ในแท็บใหม่", url_r05)

        with t3:
            try:
                components.iframe(url_r04, height=900, scrolling=True)
            except Exception:
                st.warning("ไม่สามารถฝังหน้า r04 ได้")
            st.link_button("เปิด r04 ในแท็บใหม่", url_r04)

    # ===== ขวา: วงกลม Revenue Sources (เดือนเดียว) =====
    with colRight:
        st.markdown("#### Revenue Sources (เดือนเดียว)")
        month_key = selected_month.split(' ')[0]
        idx_match = next((idx for idx in df2.index if str(idx).startswith(month_key)), None)

        if idx_match:
            vals = df2.loc[idx_match]
            max_name = vals.idxmax()

            fig_pie = px.pie(
                values=vals.values,
                names=vals.index,
                hole=.55,
                template=plotly_template,
                color=vals.index,
                color_discrete_map={
                    vals.index[0]: "#1d4ed8",
                    vals.index[1]: "#60a5fa",
                    vals.index[2]: "#10b981",
                    vals.index[3]: "#f59e0b",
                }
            )
            pulls = [0.06 if n == max_name else 0 for n in vals.index]
            fig_pie.update_traces(
                pull=pulls,
                textposition="inside",
                texttemplate="%{label}<br>%{percent:.1%}",
                hovertemplate="%{label}<br>฿%{value:,.0f} • %{percent:.1%}<extra></extra>"
            )
            total = float(vals.sum())
            fig_pie.add_annotation(
                text=f"<b>รวม</b><br>{_fmt_baht(total)}",
                x=0.5, y=0.5, showarrow=False, font=dict(size=16, color="#111827")
            )
            fig_pie.update_layout(height=900, legend_title="ช่องทาง")
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("ไม่พบข้อมูลช่องทางของเดือนนี้")
