# app.py (แทนที่บล็อกโหลดข้อมูลเดิมทั้งหมด)
import pandas as pd
import streamlit as st

try:
    loaded = load_all_data()
    if not isinstance(loaded, (list, tuple)):
        raise ValueError(f"load_all_data() คืนชนิด {type(loaded)} ที่ไม่ใช่ list/tuple")

    if len(loaded) == 6:
        df1, df2, df3, df1_melted, national_avg, month_cols = loaded

    elif len(loaded) == 5:
        # พยายามเดาว่าค่าที่หายไปคืออะไร แล้วคำนวณให้
        df1, df2, df3, df1_melted, last_item = loaded

        # เดาว่า last_item เป็น month_cols (list/tuple ของชื่อคอลัมน์)
        if isinstance(last_item, (list, tuple)) and all(isinstance(c, str) for c in last_item):
            month_cols = list(last_item)
            national_avg = df1[month_cols].mean()

        # หรือเดาว่า last_item เป็น national_average (Series)
        elif hasattr(last_item, "index") and hasattr(last_item, "shape"):
            national_avg = last_item
            # หา month_cols จาก df1
            month_cols = [c for c in df1.columns if ("2566" in c or "2567" in c)]
            if not month_cols:
                month_cols = [c for c in df1.columns if isinstance(c, str)]
            if not month_cols:
                raise ValueError("หา month_cols ไม่เจอจาก df1")

        else:
            # ไม่แน่ใจว่า last_item คืออะไร — คำนวณทั้งสองเอง
            month_cols = [c for c in df1.columns if ("2566" in c or "2567" in c)]
            if not month_cols:
                month_cols = [c for c in df1.columns if isinstance(c, str)]
            if not month_cols:
                raise ValueError("หา month_cols ไม่เจอจาก df1")
            national_avg = df1[month_cols].mean()

    else:
        raise ValueError(f"load_all_data() ต้องคืน 5 หรือ 6 ค่า แต่ได้ {len(loaded)} ค่า")

except Exception as e:
    st.error("❌ โหลดข้อมูลไม่สำเร็จจาก load_all_data()")
    st.caption("ตรวจไฟล์ utils/data.py ว่าคืนค่าครบ 6 ค่า หรือให้แอปรองรับ 5 ค่าแบบ fallback นี้แล้ว")
    st.exception(e)
    st.stop()
