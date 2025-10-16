import pandas as pd, io, json, urllib.request, streamlit as st

# ===== ใส่ CSV string ของคุณ "province_data_csv", "channel_data_csv", "product_type_data_csv" ตามต้นฉบับเดิมทั้งหมด =====
# --- (คัดลอกทั้งหมดจากโค้ดของคุณ) ---
province_data_csv = """<วาง CSV จังหวัด ทั้งหมดของคุณตรงนี้>"""
channel_data_csv  = """<วาง CSV ช่องทาง ทั้งหมดของคุณตรงนี้>"""
product_type_data_csv = """<วาง CSV ประเภทสินค้า ทั้งหมดของคุณตรงนี้>"""

PROVINCE_NAME_MAP = {
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

@st.cache_data
def load_all_data():
    df1 = pd.read_csv(io.StringIO(province_data_csv))
    df2 = pd.read_csv(io.StringIO(channel_data_csv))
    df3 = pd.read_csv(io.StringIO(product_type_data_csv))

    # เตรียม df1
    months = [c for c in df1.columns if '2566' in c or '2567' in c]
    df1.set_index('จังหวัด', inplace=True)

    # df2, df3
    df2.set_index('เดือน', inplace=True)
    df3.set_index('เดือน', inplace=True)

    # melt สำหรับแผนที่
    df1_melted = df1.reset_index().melt(id_vars='จังหวัด', var_name='เดือน', value_name='ยอดขาย')
    df1_melted['province_eng'] = df1_melted['จังหวัด'].map(PROVINCE_NAME_MAP)

    # ค่าเฉลี่ยประเทศ
    national_avg = df1[months].mean()

    return df1, df2, df3, df1_melted, national_avg

@st.cache_data
def load_geojson():
    url = "https://raw.githubusercontent.com/apisit/thailand.json/master/thailand.json"
    try:
        with urllib.request.urlopen(url) as u:
            return json.load(u)
    except Exception as e:
        st.error(f"โหลดแผนที่ประเทศไทยไม่ได้: {e}")
        return None

# export คอลัมน์เดือนให้โมดูลอื่นใช้
def _extract_month_cols():
    demo = pd.read_csv(io.StringIO(province_data_csv))
    return [c for c in demo.columns if '2566' in c or '2567' in c]

month_cols = _extract_month_cols()
