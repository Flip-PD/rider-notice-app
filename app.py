import streamlit as st
import pandas as pd

# 1. PAGE SETUP
st.set_page_config(page_title="Rider EPH Check", page_icon="🚴")
st.title("🚴 Rider EPH Status")

# 2. LOAD DATA
@st.cache_data
def load_data():
    try:
        # This reads the CSV file sitting in the same folder
        df = pd.read_csv("rider_data.csv", dtype={'RiderID': str})
        # Clean up column names (removes accidental spaces)
        df.columns = df.columns.str.strip()
        return df
    except FileNotFoundError:
        return None

df = load_data()

if df is None:
    st.error("⚠️ Data file not found. Please upload rider_data.csv to GitHub.")
    st.stop()

# 3. THE INTERFACE
rider_id = st.text_input("Enter your Rider ID")

if st.button("Check Status"):
    if rider_id:
        # Remove empty spaces from input
        clean_id = rider_id.strip()
        
        # Filter the data
        result = df[df['RiderID'] == clean_id]
        
        if not result.empty:
            # Get the EPH value
            eph_value = result.iloc[0]['EPH']
            
            # Show the Result
            st.success("✅ Access Granted")
            st.metric(label="Your Configured EPH", value=eph_value)
        else:
            st.warning("❌ ID not found. Please check your ID.")
