import streamlit as st
import pandas as pd
import time
import re

# --- 1. CONFIGURATION & ASSETS ---
st.set_page_config(
    page_title="Flipkart Minutes Rider Hub", 
    page_icon="⚡", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Image asset name (Must be uploaded to GitHub next to app.py)
LOGO_IMAGE = "flipkart-minutes-logo-hd.webp"

# Brand Colors (Reference for CSS)
# Pink: #A02047, Yellow: #FFEB3B, BG Gray: #f4f6f8

# Map CSV columns to icons and pretty labels
SLOT_CONFIG = {
    "1. Late night[00-05]":  {"time": "12 AM - 05 AM", "icon": "🌙", "label": "Late Night"},
    "2. Early Morning [06-08]": {"time": "06 AM - 08 AM", "icon": "🌅", "label": "Early Morning"},
    "3. Morning [09-11]":    {"time": "09 AM - 11 AM", "icon": "☕", "label": "Morning Peak"},
    "4. Lunch [12-14]":      {"time": "12 PM - 02 PM", "icon": "🍔", "label": "Lunch Peak"},
    "5. Early evening[15-17]": {"time": "03 PM - 05 PM", "icon": "🌤️", "label": "Afternoon"},
    "6. Evening [18-20]":    {"time": "06 PM - 08 PM", "icon": "🌆", "label": "Evening Peak"},
    "7. Night [21-23]":      {"time": "09 PM - 11 PM", "icon": "🔦", "label": "Night Slot"}
}

# --- 2. ADVANCED CSS INJECTION ---
st.markdown("""
<style>
    /* Import Inter font for a professional look */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&display=swap');

    /* Global Overrides */
    .stApp {
        background-color: #f4f6f8;
        font-family: 'Inter', sans-serif;
    }
    /* Hide default Streamlit elements */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    
    /* Custom Header Container to hold the image flush at top */
    .header-container img {
        width: 100%;
        border-bottom-left-radius: 24px;
        border-bottom-right-radius: 24px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        margin-bottom: 20px;
    }
    /* Pulls the image up to cover Streamlit padding */
    .main .block-container {
        padding-top: 0rem;
        padding-bottom: 2rem;
    }

    /* ---------- LOGIN SCREEN STYLING ---------- */
    /* Styling the input boxes to be clean white with pink focus */
    .stTextInput input {
        background-color: #ffffff !important;
        border: 2px solid #e5e7eb;
        border-radius: 12px;
        padding: 12px;
        color: #1f2937 !important; /* Dark text */
        font-weight: 600;
    }
    .stTextInput input:focus {
        border-color: #A02047;
        box-shadow: 0 0 0 3px rgba(160, 32, 71, 0.1);
    }
    /* Styling the main button */
    .stButton button {
        width: 100%;
        background: linear-gradient(135deg, #A02047 0%, #7a1535 100%);
        color: white;
        border: none;
        padding: 14px;
        border-radius: 12px;
        font-size: 16px;
        font-weight: 700;
        letter-spacing: 1px;
        transition: all 0.2s;
    }
    .stButton button:hover {
        transform: scale(1.02);
        box-shadow: 0 4px 12px rgba(160, 32, 71, 0.3);
    }

    /* ---------- DASHBOARD STYLING ---------- */
    /* Custom styles for Streamlit Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #ffffff;
        padding: 8px;
        border-radius: 16px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
    .stTabs [data-baseweb="tab"] {
        height: 40px;
        border-radius: 10px;
        font-weight: 600;
        color: #6b7280;
    }
    .stTabs [aria-selected="true"] {
        background-color: #A02047 !important;
        color: #ffffff !important;
    }

    /* User Info Card */
    .user-card {
        background: white;
        padding: 16px;
        border-radius: 16px;
        border-left: 5px solid #A02047;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }

    /* The Payout Slot Cards */
    .slot-card-container {
        background: white;
        border-radius: 18px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        border: 1px solid #f0f0f0;
        overflow: hidden;
        transition: all 0.2s ease-in-out;
        margin-bottom: 12px;
    }
    .slot-card-container:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 15px rgba(0,0,0,0.1);
        border-color: #FFEB3B;
    }
    .slot-header {
        background: #f8fafc;
        padding: 10px 15px;
        font-size: 11px;
        color: #64748b;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .slot-body {
        padding: 15px;
        text-align: center;
    }
    .slot-amount {
        font-size: 22px;
        font-weight: 900;
        color: #A02047;
        font-family: 'Inter', sans-serif;
    }
    .slot-amount span { font-size: 14px; color: #999; font-weight: 500;}

    /* Notice Board Items */
    .notice-item {
        background: white;
        padding: 16px;
        border-radius: 12px;
        border-left: 4px solid #FFEB3B;
        margin-bottom: 10px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
    .notice-badge { background: #fffbeb; color: #b45309; padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: 700; text-transform: uppercase; }

</style>
""", unsafe_allow_html=True)

# --- 3. FUNCTIONS ---

@st.cache_data
def load_data():
    try:
        creds = pd.read_csv("creds.csv", dtype=str)
        creds.columns = creds.columns.str.strip()
        
        stores = pd.read_csv("store_inputs.csv", dtype=str)
        stores.columns = stores.columns.str.strip()
        
        # CLEANING STEP: Remove existing ₹ symbols or spaces from store data
        # This prevents the double ₹₹ issue
        for col in SLOT_CONFIG.keys():
            if col in stores.columns:
                # Regex to replace anything that isn't a digit or a dot
                stores[col] = stores[col].astype(str).apply(lambda x: re.sub(r'[^\d.]', '', x))

        return creds, stores
    except Exception as e:
        return None, None

def check_login(worker_id, phone, creds_df):
    user = creds_df[creds_df['Worker_Code'] == worker_id]
    if not user.empty:
        stored_phone = str(user.iloc[0]['Phone_Number']).strip()
        input_phone = str(phone).strip()
        if stored_phone == input_phone:
            return user.iloc[0]['Hub_Name']
    return None

# --- 4. APP FLOW ---

# Initialize Session State
if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if 'hub_name' not in st.session_state: st.session_state['hub_name'] = ""
if 'worker_id' not in st.session_state: st.session_state['worker_id'] = ""

# HEADER IMAGE (Displayed using standard streamlit image but styled with CSS above)
try:
    st.markdown('<div class="header-container">', unsafe_allow_html=True)
    st.image(LOGO_IMAGE, use_column_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
except:
    st.error(f"⚠️ Missing image asset: Please upload '{LOGO_IMAGE}' to GitHub.")


creds_df, stores_df = load_data()
if creds_df is None:
    st.error("⚠️ System Error: CSV files not found.")
    st.stop()

# LOGIN LOGIC
if not st.session_state['logged_in']:
    st.markdown("<h2 style='text-align: center; font-weight: 900; color: #1f2937;'>Hello Rider! 👋</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #6b7280; margin-bottom: 30px;'>Enter your credentials to access the hub.</p>", unsafe_allow_html=True)
    
    with st.form("login_form"):
        # Using label_visibility="collapsed" to hide default labels and use placeholders
        w_code = st.text_input("Worker Code", placeholder="Worker Code (e.g., WK-1234)", label_visibility="collapsed")
        p_num = st.text_input("Phone Number", placeholder="Registered Mobile Number", label_visibility="collapsed")
        
        submitted = st.form_submit_button("SECURE LOGIN")
        
        if submitted:
            if w_code and p_num:
                with st.spinner("Verifying..."):
                    time.sleep(0.8) # Fake delay for effect
                    hub = check_login(w_code.strip(), p_num.strip(), creds_df)
                    if hub:
                        st.session_state['logged_in'] = True
                        st.session_state['hub_name'] = hub
                        st.session_state['worker_id'] = w_code
                        st.rerun()
                    else:
                        st.error("Credentials not found.")
            else:
                st.warning("Please enter both codes.")

# DASHBOARD LOGIC
else:
    hub = st.session_state['hub_name']
    store_data = stores_df[stores_df['Hub_Name'] == hub]
    
    if store_data.empty:
        st.error(f"⚠️ Hub '{hub}' data not found.")
        st.stop()

    # Fancy User Card
    st.markdown(f"""
    <div class="user-card">
        <div>
            <div style="font-size: 11px; font-weight: 700; color: #A02047; letter-spacing: 1px;">CURRENTLY LOGGED IN</div>
            <div style="font-size: 18px; font-weight: 900; color: #1f2937;">{st.session_state['worker_id']}</div>
        </div>
        <div style="text-align:right;">
             <div style="font-size: 11px; color: #9ca3af;">YOUR HUB</div>
             <div style="font-weight: 600; color: #1f2937;">📍 {hub}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Tabs for Payouts and Notices
    tab1, tab2 = st.tabs(["💰 Payout Slots", "📢 Notice Board"])

    with tab1:
        st.markdown("<br>", unsafe_allow_html=True)
        row_data = store_data.iloc[0]
        
        # Create 2-column grid layout
        col1, col2 = st.columns(2)
        cols = [col1, col2]
        col_idx = 0

        for csv_header, config in SLOT_CONFIG.items():
            if csv_header in row_data:
                # Data cleaned in load_data, so just add symbol here
                val = row_data[csv_header]
                
                card_html = f"""
                <div class="slot-card-container">
                    <div class="slot-header">
                        <span>{config['icon']}</span> {config['label']}
                        <span style="margin-left:auto; opacity: 0.7">{config['time']}</span>
                    </div>
                    <div class="slot-body">
                        <div class="slot-amount">₹{val}<span>/hr</span></div>
                    </div>
                </div>
                """
                cols[col_idx].markdown(card_html, unsafe_allow_html=True)
                # Toggle column index between 0 and 1
                col_idx = (col_idx + 1) % 2

    with tab2:
        st.markdown("<br>", unsafe_allow_html=True)
        # Placeholder "Impressive" Content
        st.markdown("""
        <div class="notice-item">
            <span class="notice-badge">Urgent · Weather</span>
            <div style="font-weight: 700; margin: 5px 0;">⛈️ Heavy Rain Alert in Sector 4</div>
            <div style="font-size: 13px; color: #4b5563;">Extra ₹20 surge bonus active from 4 PM to 7 PM today due to rain predictions. Drive safely!</div>
        </div>
        
        <div class="notice-item" style="border-left-color: #A02047;">
            <span class="notice-badge" style="color: #A02047; background: #fff1f2;">Incentive Update</span>
            <div style="font-weight: 700; margin: 5px 0;">🏆 Weekend Dhamaka is Back!</div>
            <div style="font-size: 13px; color: #4b5563;">Complete 45 orders between Sat-Sun to unlock a flat ₹500 bonus. Check your targets.</div>
             <div style="font-size: 11px; color: #9ca3af; margin-top:8px;">Posted 2 hours ago</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    if st.button("LOGOUT SECURELY"):
        for key in st.session_state.keys():
            del st.session_state[key]
        st.rerun()
