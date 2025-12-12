import streamlit as st
import pandas as pd
import time

# --- CONFIGURATION & ASSETS ---
st.set_page_config(page_title="Flipkart Minutes", page_icon="⚡", layout="centered")

# Map your CSV columns to Icons and Times
# (Make sure these keys match your CSV headers EXACTLY)
SLOT_CONFIG = {
    "1. Late night[00-05]":  {"time": "12 AM - 05 AM", "icon": "🌙", "label": "Late Night"},
    "2. Early Morning [06-08]": {"time": "06 AM - 08 AM", "icon": "🌅", "label": "Early Morning"},
    "3. Morning [09-11]":    {"time": "09 AM - 11 AM", "icon": "☕", "label": "Morning Peak"},
    "4. Lunch [12-14]":      {"time": "12 PM - 02 PM", "icon": "🍔", "label": "Lunch Peak"},
    "5. Early evening[15-17]": {"time": "03 PM - 05 PM", "icon": "🌤️", "label": "Afternoon"},
    "6. Evening [18-20]":    {"time": "06 PM - 08 PM", "icon": "🌆", "label": "Evening Peak"},
    "7. Night [21-23]":      {"time": "09 PM - 11 PM", "icon": "🔦", "label": "Night Slot"}
}

# --- CUSTOM CSS (THE UI MAGIC) ---
# This hides the standard Streamlit header and applies your "Brand Pink" styles
st.markdown("""
<style>
    /* 1. Global Reset */
    .stApp { background-color: #f4f6f8; font-family: 'Inter', sans-serif; }
    header { visibility: hidden; }
    footer { visibility: hidden; }
    
    /* 2. The Header Card */
    .brand-header {
        background: #A02047;
        padding: 20px;
        border-bottom-left-radius: 24px;
        border-bottom-right-radius: 24px;
        color: white;
        text-align: center;
        margin: -60px -20px 20px -20px; /* Pulls it to top of screen */
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .brand-title { font-size: 24px; font-weight: 900; font-style: italic; margin: 0; }
    .brand-sub { color: #FFEB3B; }
    
    /* 3. Slot Cards Grid */
    .slot-card {
        background: white;
        border-radius: 16px;
        padding: 15px;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        border: 1px solid #f3f4f6;
        margin-bottom: 10px;
        transition: transform 0.1s;
    }
    .slot-card:active { transform: scale(0.98); }
    .slot-icon { font-size: 24px; margin-bottom: 5px; }
    .slot-label { font-size: 12px; color: #6b7280; font-weight: 600; text-transform: uppercase; }
    .slot-time { font-size: 10px; background: #f3f4f6; padding: 2px 6px; border-radius: 4px; display: inline-block; margin: 5px 0; }
    .slot-val { font-size: 18px; color: #A02047; font-weight: 900; }
    
    /* 4. Inputs */
    .stTextInput input {
        border-radius: 12px;
        border: 2px solid #e5e7eb;
        padding: 10px;
    }
    .stTextInput input:focus {
        border-color: #A02047;
        box-shadow: 0 0 0 2px rgba(160, 32, 71, 0.1);
    }
    
    /* 5. Buttons */
    .stButton button {
        width: 100%;
        background-color: #A02047;
        color: white;
        border-radius: 12px;
        font-weight: 700;
        border: none;
        padding: 10px;
    }
    .stButton button:hover { background-color: #8a1c3d; color: white; }
    
    /* 6. Info Box */
    .info-box {
        background: linear-gradient(135deg, #A02047 0%, #7a1535 100%);
        color: white;
        padding: 15px;
        border-radius: 15px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# --- FUNCTIONS ---

@st.cache_data
def load_data():
    try:
        # Load Creds
        creds = pd.read_csv("creds.csv", dtype=str)
        creds.columns = creds.columns.str.strip()
        
        # Load Store Inputs
        stores = pd.read_csv("store_inputs.csv", dtype=str)
        stores.columns = stores.columns.str.strip()
        
        return creds, stores
    except Exception as e:
        return None, None

def check_login(worker_id, phone, creds_df):
    # Filter for the worker ID
    user = creds_df[creds_df['Worker_Code'] == worker_id]
    
    if not user.empty:
        # Check phone match (clean spaces)
        stored_phone = str(user.iloc[0]['Phone_Number']).strip()
        input_phone = str(phone).strip()
        
        if stored_phone == input_phone:
            return user.iloc[0]['Hub_Name']
    return None

# --- APP FLOW ---

# Initialize Session State
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'hub_name' not in st.session_state:
    st.session_state['hub_name'] = ""
if 'worker_id' not in st.session_state:
    st.session_state['worker_id'] = ""

# 1. HEADER (Always visible)
st.markdown("""
<div class="brand-header">
    <h1 class="brand-title">Flipkart <span class="brand-sub">MINUTES</span></h1>
</div>
""", unsafe_allow_html=True)

# 2. LOGIC CONTROLLER
creds_df, stores_df = load_data()

if creds_df is None:
    st.error("⚠️ System Error: CSV files not found on server.")
    st.stop()

if not st.session_state['logged_in']:
    # --- LOGIN SCREEN ---
    st.markdown("### 👋 Hello Rider!")
    st.markdown("<p style='color:#666; font-size:14px; margin-top:-15px'>Enter your details to see your slots.</p>", unsafe_allow_html=True)
    
    with st.form("login_form"):
        w_code = st.text_input("Worker Code", placeholder="e.g. WK-1029")
        p_num = st.text_input("Phone Number", placeholder="Registered Mobile Number")
        
        submitted = st.form_submit_button("CHECK IN")
        
        if submitted:
            if w_code and p_num:
                with st.spinner("Verifying Credentials..."):
                    time.sleep(1) # Fake delay for "App feel"
                    hub = check_login(w_code.strip(), p_num.strip(), creds_df)
                    
                    if hub:
                        st.session_state['logged_in'] = True
                        st.session_state['hub_name'] = hub
                        st.session_state['worker_id'] = w_code
                        st.rerun()
                    else:
                        st.error("❌ Invalid ID or Phone Number")
            else:
                st.warning("Please fill all fields")

else:
    # --- DASHBOARD SCREEN ---
    hub = st.session_state['hub_name']
    
    # Get Store Data
    store_data = stores_df[stores_df['Hub_Name'] == hub]
    
    if store_data.empty:
        st.error(f"⚠️ Hub '{hub}' not found in Store Inputs.")
        if st.button("Logout"):
            st.session_state['logged_in'] = False
            st.rerun()
        st.stop()
        
    # Welcome Banner
    st.markdown(f"""
    <div class="info-box">
        <div style="font-size:12px; opacity:0.9">LOGGED IN AS</div>
        <div style="font-size:18px; font-weight:700">{st.session_state['worker_id']}</div>
        <div style="font-size:14px; margin-top:5px">📍 Hub: {hub}</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("##### 💰 Today's Incentives")
    
    # Render Grid
    # We loop through our Config keys to find matching columns in the CSV
    
    # Create columns for the grid (2 columns wide)
    row1 = st.columns(2)
    row2 = st.columns(2)
    row3 = st.columns(2)
    row4 = st.columns(2)
    
    cols_list = [row1[0], row1[1], row2[0], row2[1], row3[0], row3[1], row4[0], row4[1]]
    current_col_idx = 0
    
    row_data = store_data.iloc[0] # The row for this hub
    
    for csv_header, config in SLOT_CONFIG.items():
        if csv_header in row_data:
            val = row_data[csv_header]
            
            # HTML Card for each slot
            card_html = f"""
            <div class="slot-card">
                <div class="slot-icon">{config['icon']}</div>
                <div class="slot-label">{config['label']}</div>
                <div class="slot-time">{config['time']}</div>
                <div class="slot-val">₹{val}</div>
            </div>
            """
            
            # Place in the grid
            if current_col_idx < len(cols_list):
                cols_list[current_col_idx].markdown(card_html, unsafe_allow_html=True)
                current_col_idx += 1
    
    st.markdown("---")
    if st.button("Logout"):
        st.session_state['logged_in'] = False
        st.rerun()
