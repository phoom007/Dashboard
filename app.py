# utils/data.py
# -*- coding: utf-8 -*-
import io
import json
import urllib.request
import pandas as pd
import streamlit as st

# --------- ใส่ CSV embedded ของคุณตามที่มีอยู่เดิม ----------
# (สรุปรายจังหวัด / ช่องทาง / ประเภทสินค้า)
from textwrap import dedent

# นี่เป็นตัวอย่าง: ให้แทนที่ 3 สตริงด้านล่างด้วยข้อมูลของคุณ (ตามที่ใช้ก่อนหน้านี้)
province_data_csv = \"\"\"{PUT_YOUR_PROVINCE_CSV_HERE}\"\"\"
channel_data_csv  = \"\"\"{PUT_YOUR_CHANNEL_CSV_HERE}\"\"\"
product_type_data_csv = \"\"\"{PUT_YOUR_PRODUCT_CSV_HERE}\"\"\"

@st.cache_data
def load_all_data():
    """
    คืนค่า 6 รายการตามลำดับ:
    df1, df2, df3, df1_melted, national_average, month_cols
    """
    # 1) อ่าน CSV จากสตริง
    try:
        df1 = pd.read_csv(io.StringIO(province_data_csv.strip()))
        df2 = pd.read_csv(io.StringIO(channel_data_csv.strip()))
        df3 = pd.read_csv(io.StringIO(product_type_data_csv.strip()))
    except Exception as e:
        raise ValueError(f"อ่าน CSV ไม่สำเร็จ: {e}")

    # 2) ตรวจคอลัมน์หลัก
    if "จังหวัด" not in df1.columns:
        raise ValueError("df1 ต้องมีคอลัมน์ 'จังหวัด'")
    if "เดือน" not in df2.columns:
        raise ValueError("df2 ต้องมีคอลัมน์ 'เดือน'")
    if "เดือน" not in df3.columns:
        raise ValueError("df3 ต้องมีคอลัมน์ 'เดือน'")

    # 3) ตั้ง index ให้ถูก
    df1 = df1.copy()
    df2 = df2.copy()
    df3 = df3.copy()
    df1.set_index("จังหวัด", inplace=True)
    df2.set_index("เดือน", inplace=True)
    df3.set_index("เดือน", inplace=True)

    # 4) หาคอลัมน์เดือนของ df1 (รองรับ '2566'/'2567')
    month_cols = [c for c in df1.columns if ("2566" in c or "2567" in c)]
    if not month_cols:
        # ถ้าไม่เจอ ให้ลองทุกคอลัมน์ที่ไม่ใช่ numeric index
        month_cols = [c for c in df1.columns if isinstance(c, str)]
    if not month_cols:
        raise ValueError("หา month_cols ไม่เจอใน df1")

    # 5) melt สำหรับแผนที่
    df1_melted = df1.reset_index().melt(id_vars="จังหวัด", var_name="เดือน", value_name="ยอดขาย")

    # 6) ค่าเฉลี่ยประเทศรายเดือน
    national_average = df1[month_cols].mean()

    return df1, df2, df3, df1_melted, national_average, month_cols


@st.cache_data
def load_geojson():
    url = "https://raw.githubusercontent.com/apisit/thailand.json/master/thailand.json"
    try:
        with urllib.request.urlopen(url) as r:
            th_geo = json.load(r)
        return th_geo
    except Exception as e:
        st.warning(f"โหลด GeoJSON ไม่สำเร็จ: {e}")
        return None
