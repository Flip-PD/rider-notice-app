import streamlit as st
import pandas as pd
import time
import re

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="Flipkart Minutes", 
    page_icon="⚡", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Asset Name (Ensure this file is in your GitHub repo)
LOGO_IMAGE = "flipkart-minutes-logo-hd.webp"

# Slot Configuration (Updated emojis to match your 3D icons)
SLOT_CONFIG = {
    "1. Late night[00-05]":  {"time": "00:00 - 05:00", "icon": "🌙", "label": "Late Night"},
    "2. Early Morning [06-08]": {"time": "06:00 - 08:00", "icon": "🌅", "label": "Early Morning"},
    "3. Morning [09-11]":    {"time": "09:00 - 11:00", "icon": "☀️", "label": "Morning"},
    "4. Lunch [12-14]":      {"time": "12:00 - 14:00", "icon": "🍛", "label": "Lunch"},
    "5. Early evening[15-17]": {"time": "15:00 - 17:00", "icon": "⛅", "label": "Early Evening"},
    "6. Evening [18-20]":    {"time": "18:00 - 20:00", "icon": "🌆", "label": "Evening"},
    "7. Night [21-23]":      {"time": "21:00 - 23:00", "icon": "🦉", "label": "Night"}
}

# --- 2. PIXEL-PERFECT CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700;800;900&display=swap');

    /* GLOBAL RESET */
    .stApp { background-color: #f4f6f8; font-family: 'Inter', sans-serif; }
    header, footer, .stDeployButton { display: none !important; }
    .block-container { padding-top: 0rem !important; padding-bottom: 2rem !important; max-width: 500px !important; }

    /* --- HEADER --- */
    /* This creates the curved maroon background */
    .header-bg {
        background-color: #A02047;
        height: 180px;
        width: 150%;
        margin-left: -25%;
        border-bottom-left-radius: 50% 20%;
        border-bottom-right-radius: 50% 20%;
        position: absolute;
        top: 0;
        z-index: 0;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }
    .logo-container {
        position: relative;
        z-index: 1;
        text-align: center;
        padding-top: 40px;
        margin-bottom: 20px;
    }
    .logo-container img { max-height: 70px; }

    /* --- LOGIN CARD (Floating White Box) --- */
    .login-card {
        background: white;
        border-radius: 24px;
        padding: 30px 24px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.08);
        position: relative;
        z-index: 2;
        margin-top: 20px;
        text-align: center;
    }
    
    .welcome-text {
        font-size: 20px;
        font-weight: 800;
        color: #A02047;
        margin-bottom: 24px;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
    }

    /* --- INPUT FIELDS (Gray Bubbles) --- */
    /* Label Styling */
    .input-label {
        font-size: 11px;
        font-weight: 800;
        color: #9ca3af;
        text-transform: uppercase;
        margin-bottom: 6px;
        display: block;
        text-align: left;
        letter-spacing: 0.5px;
    }
    
    /* The Input Box itself */
    .stTextInput input {
        background-color: #f3f4f6 !important;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 14px;
        color: #1f2937 !important;
        font-weight: 600;
        font-size: 15px;
    }
    .stTextInput input:focus {
        background-color: #ffffff !important;
        border-color: #A02047;
        box-shadow: 0 0 0 3px rgba(160, 32, 71, 0.1);
    }
    /* Hide Streamlit's default labels */
    .stTextInput label { display: none; }

    /* --- YELLOW BUTTON --- */
    .stButton button {
        background-color: #FCEE21 !important; /* Brand Yellow */
        color: #A02047 !important;
        border: none;
        border-radius: 50px; /* Pill shape */
        padding: 16px;
        font-weight: 900;
        font-size: 16px;
        letter-spacing: 1px;
        text-transform: uppercase;
        width: 100%;
        margin-top: 10px;
        box-shadow: 0 4px 10px rgba(252, 238, 33, 0.4);
        transition: transform 0.1s;
    }
    .stButton button:hover { transform: scale(1.02); }
    .stButton button:active { transform: scale(0.98); }

    /* --- DASHBOARD STYLES --- */
    
    /* User Pill */
    .user-pill {
        background: white;
        border-radius: 50px;
        padding: 12px 20px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        border: 1px solid #f0f0f0;
    }
    .user-id { font-weight: 800; font-size: 14px; color: #1f2937; }
    .user-hub { font-size: 12px; color: #6b7280; font-weight: 600; }

    /* Grid Cards */
    .grid-card {
        background: white;
        border-radius: 20px;
        padding: 16px 10px;
        text-align: center;
        box-shadow: 0 2px 5px rgba(0,0,0,0.03);
        height: 100%;
        border: 1px solid #f5f5f5;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        margin-bottom: 12px;
    }
    
    .card-icon { font-size: 28px; margin-bottom: 8px; }
    .card-label { font-size: 13px; font-weight: 800; color: #4b5563; margin-bottom: 4px; }
    
    .time-pill { 
        background: #f3f4f6; 
        color: #6b7280; 
        font-size: 10px; 
        font-weight: 700; 
        padding: 4px 10px; 
        border-radius: 12px; 
        margin-bottom: 12px; 
    }
    
    .price-text { 
        font-size: 26px; 
        font-weight: 900; 
        color: #A02047; 
        line-height: 1;
    }
    .price-sub { font-size: 12px; color: #9ca3af; font-weight: 600; }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        background-color: transparent;
        gap: 10px;
        margin-bottom: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: white;
        border-radius: 50px;
        padding: 8px 20px;
        height: auto;
        border: 1px solid #e5e7eb;
        font-weight: 700;
        font-size: 13px;
        color: #6b7280;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
    .stTabs [aria-selected="true"] {
        background-color: #A02047 !important;
        color: white !important;
        border: none;
    }
    .stTabs [data-baseweb="tab-border"] { display: none; }

</style>
<div class="header-bg"></div>
""", unsafe_allow_html=True)

# --- 3. DATA LOGIC ---
@st.cache_data
def load_data():
    try:
        creds = pd.read_csv("creds.csv", dtype=str)
        creds.columns = creds.columns.str.strip()
        stores = pd.read_csv("store_inputs.csv", dtype=str)
        stores.columns = stores.columns.str.strip()
        for col in SLOT_CONFIG.keys():
            if col in stores.columns:
                stores[col] = stores[col].astype(str).apply(lambda x: re.sub(r'[^\d.]', '', x))
        return creds, stores
    except:
        return None, None

def check_login(worker_id, phone, creds_df):
    user = creds_df[creds_df['Worker_Code'] == worker_id]
    if not user.empty:
        if str(user.iloc[0]['Phone_Number']).strip() == str(phone).strip():
            return user.iloc[0]['Hub_Name']
    return None

# --- 4. APP INTERFACE ---

if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if 'hub_name' not in st.session_state: st.session_state['hub_name'] = ""
if 'worker_id' not in st.session_state: st.session_state['worker_id'] = ""

# LOGO (Visible everywhere, floating on top of the maroon curve)
try:
    st.markdown(f'<div class="logo-container"><img src="app/static/{LOGO_IMAGE}"></div>', unsafe_allow_html=True)
except:
    pass

creds_df, stores_df = load_data()

if not st.session_state['logged_in']:
    # --- LOGIN SCREEN ---
    
    # We manually create the "Card" HTML wrapper
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    st.markdown('<div class="welcome-text">👋 Welcome Back!</div>', unsafe_allow_html=True)
    
    with st.form("login_form"):
        # Manual Labels for that "Top Left" look
        st.markdown('<span class="input-label">WORKER CODE</span>', unsafe_allow_html=True)
        w_code = st.text_input("Worker Code", placeholder="Ex: WK1234")
        
        st.markdown('<div style="height:10px"></div>', unsafe_allow_html=True) # Spacer
        
        st.markdown('<span class="input-label">PHONE NUMBER</span>', unsafe_allow_html=True)
        p_num = st.text_input("Phone Number", placeholder="Registered Mobile Number")
        
        st.markdown('<div style="height:15px"></div>', unsafe_allow_html=True) # Spacer
        
        submitted = st.form_submit_button("CHECK IN")
        
        if submitted:
            if w_code and p_num:
                hub = check_login(w_code.strip(), p_num.strip(), creds_df)
                if hub:
                    st.session_state['logged_in'] = True
                    st.session_state['hub_name'] = hub
                    st.session_state['worker_id'] = w_code
                    st.rerun()
                else:
                    st.error("Credentials not found")
            else:
                st.warning("Enter details")
    
    st.markdown('</div>', unsafe_allow_html=True) # End Card

else:
    # --- DASHBOARD SCREEN ---
    hub = st.session_state['hub_name']
    store_data = stores_df[stores_df['Hub_Name'] == hub]
    
    # 1. User Info Pill
    st.markdown(f"""
    <div class="user-pill">
        <div class="user-id">Hi, {st.session_state['worker_id']}</div>
        <div class="user-hub">📍 {hub}</div>
    </div>
    """, unsafe_allow_html=True)

    # 2. Tabs
    tab1, tab2 = st.tabs(["Payout Slots", "Notice Board"])

    with tab1:
        st.markdown("<br>", unsafe_allow_html=True)
        if not store_data.empty:
            row = store_data.iloc[0]
            
            # Grid Layout
            col1, col2 = st.columns(2)
            cols = [col1, col2]
            
            idx = 0
            for key, conf in SLOT_CONFIG.items():
                if key in row:
                    val = row[key]
                    
                    html = f"""
                    <div class="grid-card">
                        <div class="card-icon">{conf['icon']}</div>
                        <div class="card-label">{conf['label']}</div>
                        <div class="time-pill">{conf['time']}</div>
                        <div class="price-text">₹{val}<span class="price-sub">/hr</span></div>
                    </div>
                    """
                    cols[idx % 2].markdown(html, unsafe_allow_html=True)
                    idx += 1
    
    with tab2:
        st.markdown("<br>", unsafe_allow_html=True)
        st.info("📢 Notices will appear here from your Hub Manager.")
        
    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.button("LOGOUT"):
        st.session_state.clear()
        st.rerun()
