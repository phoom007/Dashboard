# ================================
# NEW 4 CHARTS (responsive to month & province)
# ================================
import numpy as np

def render_province_vs_avg_trend(
    df1,
    month_cols: List[str],
    selected_province: str,
    plotly_template="plotly_white",
    key_prefix="pvsavg",
):
    """แนวโน้มจังหวัดที่เลือก เทียบค่าเฉลี่ยประเทศ (เส้นใหญ่/ไฮไลต์ชัดเจน)"""
    st.subheader("แนวโน้มจังหวัดที่เลือกเทียบค่าเฉลี่ยประเทศ")
    nat_avg = df1[month_cols].mean()

    fig = go.Figure()

    # เส้นค่าเฉลี่ยประเทศ
    fig.add_trace(
        go.Scatter(
            x=month_cols,
            y=nat_avg.values,
            mode="lines+markers",
            name="ค่าเฉลี่ยทั้งประเทศ",
            line=dict(width=3, dash="dash", color="#7C3AED"),
            marker=dict(size=6),
            hovertemplate="%{x}<br>%{y:,.0f} บาท",
        )
    )

    # เส้นจังหวัด
    if selected_province and selected_province != "ภาพรวม" and selected_province in df1.index:
        y = df1.loc[selected_province, month_cols].values
        fig.add_trace(
            go.Scatter(
                x=month_cols,
                y=y,
                mode="lines+markers",
                name=f"{selected_province}",
                line=dict(width=5, color="#111827"),
                marker=dict(size=8),
                hovertemplate="%{x}<br>%{y:,.0f} บาท",
            )
        )
    else:
        fig.add_annotation(
            x=month_cols[-1], y=nat_avg.values[-1],
            text="เลือกจังหวัดทางซ้ายเพื่อเทียบแนวโน้ม",
            showarrow=True, arrowhead=2, ax=-40, ay=-40,
            bgcolor="rgba(255,255,255,.9)", bordercolor="#111", borderwidth=1
        )

    fig.update_layout(
        template=plotly_template,
        margin=dict(l=10, r=10, t=40, b=10),
        yaxis_title="ยอดขาย (บาท)", xaxis_title="เดือน",
        legend_title_text="",
        height=420,
        title=dict(text="Province vs National Average (Trend)", font=dict(size=20)),
        xaxis=dict(tickangle=-30, tickfont=dict(size=12)),
        yaxis=dict(tickfont=dict(size=12)),
        legend=dict(font=dict(size=12)),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False}, key=f"pvsavg_{key_prefix}")


def render_mom_change_by_province(
    df1,
    month_cols: List[str],
    selected_month: str,
    selected_province: str,
    plotly_template="plotly_white",
    key_prefix="momprov",
):
    """การเปลี่ยนแปลง MoM ตามจังหวัดสำหรับเดือนที่เลือก (ไฮไลต์จังหวัดที่เลือก)"""
    st.subheader("การเปลี่ยนแปลง MoM ตามจังหวัด (เดือนที่เลือก)")

    try:
        m_idx = month_cols.index(selected_month)
    except ValueError:
        m_idx = len(month_cols) - 1
    prev_idx = max(0, m_idx - 1)
    cur_col, prev_col = month_cols[m_idx], month_cols[prev_idx]

    cur = df1[cur_col]
    prev = df1[prev_col].replace(0, np.nan)
    mom_pct = ((cur - prev) / prev * 100).fillna(0).sort_values(ascending=True)

    colors = []
    for prov in mom_pct.index:
        if selected_province and selected_province != "ภาพรวม" and prov == selected_province:
            colors.append("#111827")  # ไฮไลต์จังหวัดที่เลือก
        else:
            colors.append("#60A5FA" if mom_pct.loc[prov] >= 0 else "#F87171")

    fig = go.Figure(go.Bar(
        x=mom_pct.values,
        y=mom_pct.index,
        orientation="h",
        marker=dict(color=colors),
        text=[f"{v:.2f}%" for v in mom_pct.values],
        textposition="outside",
    ))
    fig.update_layout(
        template=plotly_template,
        margin=dict(l=10, r=10, t=40, b=10),
        xaxis_title="เปอร์เซ็นต์เปลี่ยนแปลง MoM (%)",
        yaxis_title="",
        height=600,
        title=dict(text=f"MoM Change by Province — {selected_month}", font=dict(size=20)),
        xaxis=dict(tickfont=dict(size=12)), yaxis=dict(tickfont=dict(size=12)),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False}, key=f"momprov_{key_prefix}")


def render_monthly_heatmap_selected(
    df1,
    month_cols: List[str],
    selected_month: str,
    selected_province: str,
    plotly_template="plotly_white",
    key_prefix="heat",
):
    """Heatmap: Top 15 จังหวัด (ตามยอดของเดือนที่เลือก) x ทุกเดือน — ไฟอ่านชัดเจน"""
    st.subheader("Heatmap จังหวัดยอดนิยม (Top 15) ตามเดือน")

    # เลือก Top 15 โดยดูค่าของเดือนที่เลือก
    if selected_month not in df1.columns:
        st.info("ไม่พบข้อมูลเดือนที่เลือกใน df1", icon="ℹ️")
        return
    top15 = df1[selected_month].sort_values(ascending=False).head(15).index.tolist()
    sub = df1.loc[top15, month_cols]

    fig = px.imshow(
        sub.values,
        x=month_cols,
        y=top15,
        labels=dict(color="ยอดขาย (บาท)"),
        color_continuous_scale="YlGnBu",
        aspect="auto",
    )
    fig.update_layout(
        template=plotly_template,
        margin=dict(l=10, r=10, t=40, b=10),
        height=520,
        title=dict(text=f"Heatmap — Top 15 จังหวัด (อิง {selected_month})", font=dict(size=20)),
        xaxis=dict(tickangle=-30),
        coloraxis_colorbar=dict(title="บาท"),
    )

    # ขีดเส้น/annotation ที่จังหวัดเลือก
    if selected_province and selected_province in top15:
        sel_idx = top15.index(selected_province)
        fig.add_annotation(
            x=month_cols[-1],
            y=sel_idx,
            text=f"เลือก: {selected_province}",
            showarrow=True, arrowhead=2, ax=40, ay=0,
            bgcolor="rgba(255,255,255,.95)", bordercolor="#111", borderwidth=1
        )

    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False}, key=f"heat_{key_prefix}")


def render_channel_cumulative_ytd(
    df2,
    month_cols: List[str],
    selected_month: str,
    plotly_template="plotly_white",
    key_prefix="cumch",
):
    """กราฟเส้นสะสม (YTD) ของช่องทาง — คำนวณตั้งแต่ต้นปีงบจนถึงเดือนที่เลือก"""
    st.subheader("Channel YTD (สะสมจนถึงเดือนที่เลือก)")

    # หา index ของเดือนที่เลือกใน df2 (ใช้ prefix ของเดือนภาษาไทย)
    month_key = selected_month.split(" ")[0]
    idx_match = next((i for i in df2.index if str(i).startswith(month_key)), None)
    if idx_match is None:
        st.info("ไม่พบเดือนที่เลือกในตารางช่องทาง", icon="ℹ️")
        return
    pos = df2.index.tolist().index(idx_match)
    d2 = df2.iloc[: pos + 1].copy()  # ตั้งแต่ต้นปีงบถึงเดือนที่เลือก

    # ทำ cumulative ต่อคอลัมน์ (ทุกช่องทาง)
    cum = d2.cumsum()
    cum["เดือน"] = d2.index
    long_df = cum.reset_index(drop=True).melt(id_vars="เดือน", var_name="ช่องทาง", value_name="สะสมบาท")

    fig = px.line(
        long_df, x="เดือน", y="สะสมบาท", color="ช่องทาง",
        template=plotly_template
    )
    fig.update_traces(mode="lines+markers", hovertemplate="%{x}<br>%{y:,.0f} บาท")
    fig.update_layout(
        margin=dict(l=10, r=10, t=40, b=10),
        yaxis_title="ยอดสะสม (บาท)",
        xaxis_title="เดือน",
        title=dict(text=f"ยอดสะสม YTD ตามช่องทาง — ถึง {selected_month}", font=dict(size=20)),
        xaxis=dict(tickangle=-30, tickfont=dict(size=12)),
        yaxis=dict(tickfont=dict(size=12)),
        legend=dict(font=dict(size=12)),
        height=420
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False}, key=f"cumch_{key_prefix}")
