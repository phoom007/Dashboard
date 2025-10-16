# utils/theme.py
import streamlit as st
def set_base_page_config():
    st.set_page_config(page_title="OTOP Sales Dashboard", page_icon="🛍️", layout="wide")
def get_plotly_template():
    return "plotly_white"
def inject_global_css():
    st.markdown("""<style>/* CSS ตามที่ตั้งค่าไว้ */</style>""", unsafe_allow_html=True)
