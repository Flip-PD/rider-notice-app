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

# Asset Name (Must be in GitHub)
LOGO_IMAGE = "flipkart-minutes-logo-hd.webp"

# Slot Configuration
SLOT_CONFIG = {
    "1. Late night[00-05]":  {"time": "12 AM - 05 AM", "icon": "🌙", "label": "Late Night"},
    "2. Early Morning [06-08]": {"time": "06 AM - 08 AM", "icon": "🌅", "label": "Early Morning"},
    "3. Morning [09-11]":    {"time": "09 AM - 11 AM", "icon": "☕", "label": "Morning Peak"},
    "4. Lunch [12-14]":      {"time": "12 PM - 02 PM", "icon": "🍔", "label": "Lunch Peak"},
    "5. Early evening[15-17]": {"time": "03 PM - 05 PM", "icon": "🌤️", "label": "Afternoon"},
    "6. Evening [18-20]":    {"time": "06 PM - 08 PM", "icon": "🌆", "label": "Evening Peak"},
    "7. Night [21-23]":      {"time": "09 PM - 11 PM", "icon": "🔦", "label": "Night Slot"}
}

# --- 2. ADVANCED CSS (MOBILE OPTIMIZED) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700;900&display=swap');

    /* --- GLOBAL RESET --- */
    .stApp { background-color: #f4f6f8; font-family: 'Inter', sans-serif; }
    header, footer, .stDeployButton { display: none !important; }
    
    /* Pull content to top */
    .block-container { padding-top: 1rem !important; padding-bottom: 2rem !important; }

    /* --- HEADER IMAGE --- */
    .header-wrapper {
        display: flex;
        justify-content: center;
        background: #A02047;
        margin: -1rem -5rem 1.5rem -5rem; /* Negative margins to stretch full width */
        padding: 10px 0 20px 0;
        border-bottom-left-radius: 24px;
        border-bottom-right-radius: 24px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }
    .header-wrapper img {
        max-height: 80px; /* Constrains height to prevent scrolling */
        object-fit: contain;
    }

    /* --- LOGIN INPUTS --- */
    .stTextInput label { display: none; } /* Hide default labels */
    .stTextInput input {
        background-color: #ffffff !important;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 12px 15px;
        font-size: 16px; /* Prevents iOS zoom on focus */
        color: #111827 !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
    .stTextInput input:focus {
        border-color: #A02047;
        box-shadow: 0 0 0 3px rgba(160, 32, 71, 0.15);
    }

    /* --- BUTTONS --- */
    .stButton button {
        width: 100%;
        background: #A02047;
        color: white;
        border: none;
        padding: 12px;
        border-radius: 12px;
        font-weight: 700;
        font-size: 16px;
        box-shadow: 0 4px 6px rgba(160, 32, 71, 0.2);
        transition: transform 0.1s;
    }
    .stButton button:hover { transform: scale(1.01); background: #8a1c3d; }
    .stButton button:active { transform: scale(0.97); }

    /* --- RESPONSIVE USER CARD --- */
    .user-card {
        background: white;
        padding: 16px;
        border-radius: 16px;
        border-left: 5px solid #A02047;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 15px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    /* MOBILE TWEAK: Stack info on small screens */
    @media (max-width: 400px) {
        .user-card { flex-direction: column; align-items: flex-start; gap: 10px; }
        .user-hub-info { text-align: left !important; }
    }

    .user-label { font-size: 10px; font-weight: 700; color: #9ca3af; letter-spacing: 0.5px; text-transform: uppercase; }
    .user-value { font-size: 16px; font-weight: 800; color: #1f2937; }
    .user-hub-info { text-align: right; }

    /* Pulsing Dot Animation */
    .live-dot {
        height: 8px; width: 8px;
        background-color: #22c55e;
        border-radius: 50%;
        display: inline-block;
        margin-right: 4px;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.7); }
        70% { box-shadow: 0 0 0 6px rgba(34, 197, 94, 0); }
        100% { box-shadow: 0 0 0 0 rgba(34, 197, 94, 0); }
    }

    /* --- TABS --- */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0px;
        background-color: #ffffff;
        padding: 4px;
        border-radius: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        display: flex;
        width: 100%;
    }
    .stTabs [data-baseweb="tab"] {
        flex: 1; /* Force equal width */
        height: 40px;
        border-radius: 8px;
        font-weight: 600;
        font-size: 14px;
        color: #6b7280;
        border: none !important;
        background: transparent;
    }
    .stTabs [aria-selected="true"] {
        background-color: #fffbeb !important; /* Light Yellow bg */
        color: #A02047 !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.1);
    }
    .stTabs [data-baseweb="tab-border"] { display: none; } /* Hide blue underline */

    /* --- SLOT CARDS --- */
    .slot-card {
        background: white;
        border-radius: 16px;
        border: 1px solid #f3f4f6;
        overflow: hidden;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        margin-bottom: 8px;
    }
    .slot-header {
        background: #f9fafb;
        padding: 8px 12px;
        font-size: 10px;
        color: #4b5563; /* Darker gray for visibility */
        font-weight: 700;
        text-transform: uppercase;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid #f3f4f6;
    }
    .slot-body { padding: 10px; text-align: center; }
    .slot-amount { font-size: 20px; font-weight: 900; color: #A02047; }
    .slot-sub { font-size: 11px; color: #9ca3af; font-weight: 500; }

    /* --- NOTICES --- */
    .notice-card {
        background: white;
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #f3f4f6;
        border-left: 4px solid #F59E0B; /* Orange-Yellow */
        margin-bottom: 12px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.03);
    }
    .notice-tag {
        background: #FFFBEB; color: #B45309;
        padding: 2px 6px; border-radius: 4px;
        font-size: 9px; font-weight: 800; text-transform: uppercase;
    }
    .notice-title {
        font-size: 14px; font-weight: 700; color: #1f2937; /* Dark black */
        margin: 6px 0 4px 0;
    }
    .notice-body { font-size: 12px; color: #4b5563; line-height: 1.4; }
    .notice-time { font-size: 10px; color: #9ca3af; margin-top: 8px; display: block;}

</style>
""", unsafe_allow_html=True)

# --- 3. LOGIC ---

@st.cache_data
def load_data():
    try:
        creds = pd.read_csv("creds.csv", dtype=str)
        creds.columns = creds.columns.str.strip()
        stores = pd.read_csv("store_inputs.csv", dtype=str)
        stores.columns = stores.columns.str.strip()
        # Clean currency symbols
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

# Initialize State
if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if 'hub_name' not in st.session_state: st.session_state['hub_name'] = ""
if 'worker_id' not in st.session_state: st.session_state['worker_id'] = ""

# --- HEADER (Visible everywhere) ---
try:
    st.markdown(f'<div class="header-wrapper"><img src="app/static/{LOGO_IMAGE}" alt="Logo"></div>', unsafe_allow_html=True)
    # Note: If image breaks locally, use simple st.image, but the CSS above targets the wrapper.
    # Fallback for Streamlit Cloud specific pathing usually requires standard st.image for simple usage:
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.image(LOGO_IMAGE, use_column_width=True)
except:
    pass 

# --- MAIN LOGIC ---
creds_df, stores_df = load_data()

if not st.session_state['logged_in']:
    # LOGIN SCREEN
    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True) # Spacer
    st.markdown("### 👋 Hello Rider!")
    st.markdown("<p style='color:#6b7280; font-size:14px; margin-top:-10px; margin-bottom: 25px'>Enter your details to check your slots.</p>", unsafe_allow_html=True)
    
    with st.form("login"):
        w_code = st.text_input("Worker Code", placeholder="Worker Code (e.g. WK-1029)")
        p_num = st.text_input("Phone Number", placeholder="Registered Phone Number")
        if st.form_submit_button("CHECK IN"):
            if w_code and p_num:
                hub = check_login(w_code.strip(), p_num.strip(), creds_df)
                if hub:
                    st.session_state['logged_in'] = True
                    st.session_state['hub_name'] = hub
                    st.session_state['worker_id'] = w_code
                    st.rerun()
                else:
                    st.error("Invalid Login Credentials")
            else:
                st.warning("Please enter all details")

else:
    # DASHBOARD
    hub = st.session_state['hub_name']
    store_data = stores_df[stores_df['Hub_Name'] == hub]
    
    # Responsive User Card
    st.markdown(f"""
    <div class="user-card">
        <div>
            <div class="user-label">Logged In As</div>
            <div class="user-value">{st.session_state['worker_id']}</div>
        </div>
        <div class="user-hub-info">
             <div class="user-label">Current Hub</div>
             <div class="user-value" style="color: #4b5563; font-weight:600; font-size:14px">
                <span class="live-dot"></span>{hub}
             </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Tabs
    tab1, tab2 = st.tabs(["Payout Slots", "Notice Board"])

    with tab1:
        st.markdown("<div style='height: 10px'></div>", unsafe_allow_html=True)
        if not store_data.empty:
            row = store_data.iloc[0]
            
            # Grid system
            col1, col2 = st.columns(2)
            cols = [col1, col2]
            
            idx = 0
            for key, conf in SLOT_CONFIG.items():
                if key in row:
                    val = row[key]
                    html = f"""
                    <div class="slot-card">
                        <div class="slot-header">
                            <span>{conf['icon']} {conf['label']}</span>
                        </div>
                        <div class="slot-body">
                            <div class="slot-amount">₹{val}</div>
                            <div class="slot-sub">{conf['time']}</div>
                        </div>
                    </div>
                    """
                    cols[idx % 2].markdown(html, unsafe_allow_html=True)
                    idx += 1

    with tab2:
        st.markdown("<div style='height: 10px'></div>", unsafe_allow_html=True)
        # Notices
        st.markdown("""
        <div class="notice-card">
            <span class="notice-tag">⚠️ WEATHER UPDATE</span>
            <div class="notice-title">Heavy Rain Surge Active</div>
            <div class="notice-body">Extra ₹20 per order is active from 4 PM to 8 PM today due to heavy rain forecast.</div>
            <span class="notice-time">Posted 1 hour ago</span>
        </div>
        
        <div class="notice-card" style="border-left-color: #A02047;">
             <span class="notice-tag" style="background: #fdf2f8; color: #be185d;">🏆 RIDER OF THE WEEK</span>
            <div class="notice-title">Congratulations Rahul K.</div>
            <div class="notice-body">Top performer of the week with 100% login hours! Collect your reward from the Hub Manager.</div>
            <span class="notice-time">Posted Yesterday</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("LOGOUT"):
        st.session_state.clear()
        st.rerun()
