import streamlit as st
import time
import requests
from dhanhq import dhanhq
import google.generativeai as genai
from datetime import datetime

# --- App Interface Settings ---
st.set_page_config(page_title="SMC AI Trader", page_icon="📈", layout="centered")

st.title("🚀 SMC AI Mobile Dashboard")
st.subheader("Dhan + Gemini Live Analysis")

# --- Sidebar: API Keys ---
with st.sidebar:
    st.header("🔑 API Setup")
    client_id = st.text_input("Dhan Client ID", value="1109282855")
    access_token = st.text_input("Dhan Access Token", type="password")
    gemini_key = st.text_input("Gemini API Key", type="password")

# --- Backend Logic ---
if st.button("Start Live Tracking"):
    if not access_token or not gemini_key:
        st.error("Bhai, Token aur Key toh daalo!")
    else:
        # Initializing Connections
        dhan = dhanhq(client_id, access_token)
        genai.configure(api_key=gemini_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        st.success("System Live Ho Gaya Hai! Kal 9:15 AM par data refresh hoga.")
        
        # Placeholder for live data
        price_col, zone_col = st.columns(2)
        with price_col:
            nifty_placeholder = st.empty()
        with zone_col:
            status_placeholder = st.empty()
            
        ai_suggestion = st.empty()

        # Simple Loop (Streamlit style)
        while True:
            try:
                # 1. Fetch Nifty Data
                resp = dhan.get_ltp_data("NSE_INDEX", "INDEX", 13)
                if resp['status'] == 'success':
                    price = resp['data']['last_price']
                    nifty_placeholder.metric("NIFTY 50", f"₹{price}")
                    
                    # 2. Get Gemini Analysis
                    prompt = f"Nifty is at {price}. Based on 3B'S rules (Bias, Base, Below/Above), what is the plan? Answer in short Hindi."
                    response = model.generate_content(prompt)
                    
                    # 3. Update Dashboard
                    ai_suggestion.info(f"🤖 Gemini Plan: {response.text}")
                    
                    # 4. Premium/Discount Logic (Simple)
                    # Maan lo equilibrium 24300 hai (Example ke liye)
                    if price < 24300:
                        status_placeholder.warning("Zone: DISCOUNT 🟢")
                    else:
                        status_placeholder.error("Zone: PREMIUM 🔴")
                        
                else:
                    st.error("Dhan API Connection Error!")
                
                # Sleep for 60 seconds
                import time
                time.sleep(60)
                st.rerun() # Refreshing the app
                
            except Exception as e:
                st.write(f"Wait... {e}")
                time.sleep(10)
