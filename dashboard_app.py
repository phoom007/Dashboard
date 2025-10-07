# ==============================================================================
# ส่วนที่ 1: การนำเข้าไลบรารีและตั้งค่าหน้าเว็บ
# ==============================================================================
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import urllib.request

# ตั้งค่าหน้าเว็บให้เป็นแบบ Wide Mode และกำหนดชื่อ/ไอคอน
st.set_page_config(
    page_title="OTOP Sales Dashboard",
    page_icon="🛍️",
    layout="wide"
)

# ==============================================================================
# ส่วนที่ 2: CSS สำหรับการออกแบบสไตล์ (Dark/Light Mode, Rounded Corners)
# ==============================================================================
def load_css():
    # CSS สำหรับ Light Mode
    css_light = """
    <style>
        /* --- การ์ด KPI --- */
        .kpi-card {
            background-color: #FFFFFF;
            padding: 1.5rem;
            border-radius: 15px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            border: 1px solid #E0E0E0;
            transition: all 0.3s ease-in-out;
        }
        .kpi-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 20px rgba(0,0,0,0.12);
        }
        .kpi-title {
            font-size: 1rem;
            font-weight: 600;
            color: #4F4F4F;
            margin-bottom: 0.5rem;
        }
        .kpi-value {
            font-size: 2.2rem;
            font-weight: 700;
            color: #1A237E; /* สีน้ำเงินเข้ม */
        }
        .kpi-delta {
            font-size: 0.9rem;
            color: #828282;
        }

        /* --- กรอบเนื้อหาในแท็บ --- */
        .content-box {
            background-color: #F8F9FA;
            padding: 1rem;
            border-radius: 15px;
            border: 1px solid #E0E0E0;
        }
    </style>
    """

    # CSS สำหรับ Dark Mode
    css_dark = """
    <style>
        /* --- การ์ด KPI --- */
        .kpi-card {
            background-color: #1E1E1E; /* สีพื้นหลังการ์ด */
            padding: 1.5rem;
            border-radius: 15px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            border: 1px solid #424242;
            transition: all 0.3s ease-in-out;
        }
        .kpi-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 20px rgba(0,0,0,0.5);
            border: 1px solid #757575;
        }
        .kpi-title {
            font-size: 1rem;
            font-weight: 600;
            color: #BDBDBD; /* สีตัวอักษร title */
            margin-bottom: 0.5rem;
        }
        .kpi-value {
            font-size: 2.2rem;
            font-weight: 700;
            color: #90CAF9; /* สีฟ้าสว่าง */
        }
        .kpi-delta {
            font-size: 0.9rem;
            color: #9E9E9E;
        }
        /* --- กรอบเนื้อหาในแท็บ --- */
        .content-box {
            background-color: #2C2C2C;
            padding: 1rem;
            border-radius: 15px;
            border: 1px solid #424242;
        }
    </style>
    """
    # ตรวจสอบ theme ที่เลือกและใส่ CSS ที่เหมาะสม
    if st.session_state.theme == "Dark":
        st.markdown(css_dark, unsafe_allow_html=True)
    else:
        st.markdown(css_light, unsafe_allow_html=True)


# ==============================================================================
# ส่วนที่ 3: การโหลดและเตรียมข้อมูล
# ==============================================================================
@st.cache_data
def load_all_data():
    # โหลดข้อมูลจากไฟล์ CSV
    df1 = pd.read_csv('sales_by_province.csv')
    df2 = pd.read_csv('sales_by_channel.csv')
    df3 = pd.read_csv('sales_by_product_type.csv')

    # --- เตรียม DF1 (ยอดขายรายจังหวัด) ---
    month_cols = [col for col in df1.columns if '2566' in col or '2567' in col]
    df1.set_index('จังหวัด', inplace=True)

    # --- เตรียม DF2 (ช่องทาง) ---
    df2.set_index('เดือน', inplace=True)
    
    # --- เตรียม DF3 (ประเภทสินค้า) ---
    df3.set_index('เดือน', inplace=True)
    
    # --- เตรียมข้อมูล Melted สำหรับแผนที่ ---
    df1_melted = df1.reset_index().melt(id_vars='จังหวัด', var_name='เดือน', value_name='ยอดขาย')
    
    # --- คำนวณค่าเฉลี่ยประเทศ ---
    national_average = df1[month_cols].mean()
    
    return df1, df2, df3, df1_melted, national_average, month_cols

@st.cache_data
def load_geojson():
    geojson_url = "https://raw.githubusercontent.com/apisit/thailand.json/master/thailand.json"
    try:
        with urllib.request.urlopen(geojson_url) as url:
            thailand_geojson = json.load(url)
        return thailand_geojson
    except Exception as e:
        st.error(f"ไม่สามารถโหลดแผนที่ประเทศไทยได้: {e}")
        return None

# โหลดข้อมูลทั้งหมด
try:
    df1, df2, df3, df1_melted, national_average, month_cols = load_all_data()
    thailand_geojson = load_geojson()
except FileNotFoundError:
    st.error("ไม่พบไฟล์ข้อมูล .csv! กรุณาตรวจสอบว่าไฟล์ข้อมูลทั้ง 3 ไฟล์อยู่ในโฟลเดอร์เดียวกับ `dashboard_app.py`")
    st.stop()


# Mapping ชื่อจังหวัด ไทย -> อังกฤษ สำหรับแผนที่
province_name_map = {
    'กรุงเทพมหานคร': 'Bangkok', 'สมุทรปราการ': 'Samut Prakan', 'นนทบุรี': 'Nonthaburi', 'ปทุมธานี': 'Pathum Thani',
    'พระนครศรีอยุธยา': 'Phra Nakhon Si Ayutthaya', 'อ่างทอง': 'Ang Thong', 'ลพบุรี': 'Lopburi', 'สิงห์บุรี': 'Sing Buri',
    'ชัยนาท': 'Chai Nat', 'สระบุรี': 'Saraburi', 'ชลบุรี': 'Chon Buri', 'ระยอง': 'Rayong', 'จันทบุรี': 'Chanthaburi',
    'ตราด': 'Trat', 'ฉะเชิงเทรา': 'Chachoengsao', 'ปราจีนบุรี': 'Prachin Buri', 'นครนายก': 'Nakhon Nayok',
    'สระแก้ว': 'Sa Kaeo', 'นครราชสีมา': 'Nakhon Ratchasima', 'บุรีรัมย์': 'Buri Ram', 'สุรินทร์': 'Surin',
    'ศรีสะเกษ': 'Si Sa Ket', 'อุบลราชธานี': 'Ubon Ratchathani', 'ยโสธร': 'Yasothon', 'ชัยภูมิ': 'Chaiyaphum',
    'อำนาจเจริญ': 'Amnat Charoen', 'หนองบัวลำภู': 'Nong Bua Lam Phu', 'ขอนแก่น': 'Khon Kaen', 'อุดรธานี': 'Udon Thani',
    'เลย': 'Loei', 'หนองคาย': 'Nong Khai', 'มหาสารคาม': 'Maha Sarakham', 'ร้อยเอ็ด': 'Roi Et', 'กาฬสินธุ์': 'Kalasin',
    'สกลนคร': 'Sakon Nakhon', 'นครพนม': 'Nakhon Phanom', 'มุกดาหาร': 'Mukdahan', 'เชียงใหม่': 'Chiang Mai',
    'ลำพูน': 'Lamphun', 'ลำปาง': 'Lampang', 'อุตรดิตถ์': 'Uttaradit', 'แพร่': 'Phrae', 'น่าน': 'Nan',
    'พะเยา': 'Phayao', 'เชียงราย': 'Chiang Rai', 'แม่ฮ่องสอน': 'Mae Hong Son', 'นครสวรรค์': 'Nakhon Sawan',
    'อุทัยธานี': 'Uthai Thani', 'กำแพงเพชร': 'Kamphaeng Phet', 'ตาก': 'Tak', 'สุโขทัย': 'Sukhothai',
    'พิษณุโลก': 'Phitsanulok', 'พิจิตร': 'Phichit', 'เพชรบูรณ์': 'Phetchabun', 'ราชบุรี': 'Ratchaburi',
    'กาญจนบุรี': 'Kanchanaburi', 'สุพรรณบุรี': 'Suphan Buri', 'นครปฐม': 'Nakhon Pathom', 'สมุทรสาคร': 'Samut Sakhon',
    'สมุทรสงคราม': 'Samut Songkhram', 'เพชรบุรี': 'Phetchaburi', 'ประจวบคีรีขันธ์': 'Prachuap Khiri Khan',
    'นครศรีธรรมราช': 'Nakhon Si Thammarat', 'กระบี่': 'Krabi', 'พังงา': 'Phangnga', 'ภูเก็ต': 'Phuket',
    'สุราษฎร์ธานี': 'Surat Thani', 'ระนอง': 'Ranong', 'ชุมพร': 'Chumphon', 'สงขลา': 'Songkhla', 'สตูล': 'Satun',
    'ตรัง': 'Trang', 'พัทลุง': 'Phatthalung', 'ปัตตานี': 'Pattani', 'ยะลา': 'Yala', 'นราธิวาส': 'Narathiwat',
    'บึงกาฬ': 'Bueng Kan'
}
df1_melted['province_eng'] = df1_melted['จังหวัด'].map(province_name_map)

# ==============================================================================
# ส่วนที่ 4: ส่วนควบคุมและแสดงผลของเว็บ (UI)
# ==============================================================================

# --- ตัวควบคุม (Filters) และ Theme Toggle ที่ Sidebar ---
st.sidebar.header("🎨 การแสดงผลและตัวกรอง")

# Theme Toggle
if 'theme' not in st.session_state:
    st.session_state.theme = "Light"

theme_mode = st.sidebar.radio(
    "เลือกธีม:",
    ["Light", "Dark"],
    index=0 if st.session_state.theme == "Light" else 1,
    key="theme_selector"
)
st.session_state.theme = theme_mode
load_css() # โหลด CSS ตาม theme ที่เลือก

# กำหนด template ของ Plotly ตาม theme
theme_plotly = "plotly_white" if st.session_state.theme == "Light" else "plotly_dark"


# Filters
selected_month = st.sidebar.selectbox(
    'เลือกเดือน:',
    options=month_cols,
    index=len(month_cols)-1 # เลือกเดือนล่าสุดเป็นค่าเริ่มต้น
)
selected_province = st.sidebar.selectbox(
    'เลือกจังหวัด (เพื่อดูแนวโน้ม):',
    options=['ภาพรวม'] + df1.index.tolist()
)

# --- ส่วนหัว Dashboard ---
st.title("🛍️ Dashboard สรุปผลการจำหน่ายสินค้า OTOP")
st.markdown(f"ข้อมูลประจำเดือน **{selected_month}**")

# --- การ์ดสรุปตัวเลขสำคัญ (KPI Cards) ---
st.markdown("---")
# คำนวณค่า KPI
total_sales_month = df1[selected_month].sum()
top_province_month = df1[selected_month].idxmax()
top_province_sales = df1[selected_month].max()

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">ยอดขายรวมทั้งประเทศ</div>
        <div class="kpi-value">฿{total_sales_month:,.0f}</div>
        <div class="kpi-delta">สำหรับเดือน {selected_month}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">จังหวัดที่มียอดขายสูงสุด</div>
        <div class="kpi-value">{top_province_month}</div>
        <div class="kpi-delta">ยอดขาย: ฿{top_province_sales:,.0f}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    # หาประเภทสินค้าที่ขายดีที่สุด
    month_key = selected_month.split(' ')[0]
    idx_match = next((idx for idx in df3.index if str(idx).startswith(month_key)), None)
    if idx_match:
        top_product_type = df3.loc[idx_match].idxmax()
        top_product_sales = df3.loc[idx_match].max()
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">ประเภทสินค้าขายดีที่สุด</div>
            <div class="kpi-value">{top_product_type}</div>
            <div class="kpi-delta">ยอดขาย: ฿{top_product_sales:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True) # เว้นวรรค

# --- แท็บแสดงผล ---
tab1, tab2 = st.tabs(["📊 ภาพรวมรายจังหวัด", "📈 วิเคราะห์เชิงลึก"])

with tab1:
    st.subheader(f'ยอดขาย OTOP รายจังหวัด ประจำเดือน {selected_month}')
    
    col1_tab1, col2_tab1 = st.columns([3, 2]) # แบ่งคอลัมน์ในแท็บ อัตราส่วน 3:2

    with col1_tab1:
        st.markdown("##### แผนที่แสดงยอดขายรายจังหวัด")
        _map_df = df1_melted[df1_melted['เดือน'] == selected_month].dropna(subset=['province_eng'])

        if thailand_geojson is not None and not _map_df.empty:
            fig_map = px.choropleth_mapbox(
                _map_df,
                geojson=thailand_geojson,
                locations='province_eng',
                featureidkey="properties.name",
                color='ยอดขาย',
                color_continuous_scale="Viridis",
                mapbox_style="carto-positron" if st.session_state.theme == "Light" else "carto-darkmatter",
                center={"lat": 13.736717, "lon": 100.523186},
                zoom=4.5,
                opacity=0.6
            )
            fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
            st.plotly_chart(fig_map, use_container_width=True)
        else:
            st.info("ไม่สามารถแสดงแผนที่ได้")

    with col2_tab1:
        st.markdown("##### 20 อันดับจังหวัดยอดขายสูงสุด")
        monthly_data = df1[[selected_month]].sort_values(by=selected_month, ascending=False).reset_index()
        
        fig_bar = px.bar(
            monthly_data.head(20).sort_values(by=selected_month, ascending=True),
            x=selected_month,
            y='จังหวัด',
            orientation='h',
            labels={'จังหวัด': '', selected_month: 'ยอดขาย (บาท)'},
            template=theme_plotly,
            height=600
        )
        fig_bar.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_bar, use_container_width=True)


with tab2:
    st.subheader(f'การวิเคราะห์แนวโน้มและสัดส่วนยอดขาย')
    
    # --- กราฟแนวโน้ม ---
    st.markdown(f"##### แนวโน้มยอดขายของ: **{selected_province}**")
    fig_line = go.Figure()
    if selected_province != 'ภาพรวม':
        fig_line.add_trace(go.Scatter(x=month_cols, y=df1.loc[selected_province], mode='lines+markers', name=selected_province))

    fig_line.add_trace(go.Scatter(x=month_cols, y=national_average, mode='lines', name='ค่าเฉลี่ยทั้งประเทศ', line=dict(dash='dash')))
    fig_line.update_layout(
        xaxis_title='เดือน', yaxis_title='ยอดขาย (บาท)', xaxis_tickangle=-45, height=400,
        template=theme_plotly,
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
    )
    st.plotly_chart(fig_line, use_container_width=True)
    
    st.markdown("---")
    
    col1_tab2, col2_tab2 = st.columns(2)
    
    with col1_tab2:
        # --- กราฟช่องทาง ---
        st.markdown(f"##### สัดส่วนยอดขายตามช่องทาง ({selected_month})")
        month_key = selected_month.split(' ')[0]
        idx_match = next((idx for idx in df2.index if str(idx).startswith(month_key)), None)
        if idx_match:
            channel_data = df2.loc[idx_match]
            fig_pie_channel = px.pie(
                values=channel_data.values,
                names=channel_data.index,
                hole=.4,
                template=theme_plotly,
                title=""
            )
            st.plotly_chart(fig_pie_channel, use_container_width=True)
        else:
            st.info("ไม่พบข้อมูลช่องทางสำหรับเดือนที่เลือก")
            
    with col2_tab2:
        # --- กราฟประเภทสินค้า ---
        st.markdown(f"##### สัดส่วนยอดขายตามประเภทสินค้า ({selected_month})")
        month_key = selected_month.split(' ')[0]
        idx_match = next((idx for idx in df3.index if str(idx).startswith(month_key)), None)
        if idx_match:
            product_data = df3.loc[idx_match]
            fig_pie_product = px.pie(
                values=product_data.values,
                names=product_data.index,
                hole=.4,
                template=theme_plotly,
                title=""
            )
            st.plotly_chart(fig_pie_product, use_container_width=True)
        else:
            st.info("ไม่พบข้อมูลประเภทสินค้าสำหรับเดือนที่เลือก")
