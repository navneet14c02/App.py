import streamlit as st
import time
import requests
from dhanhq import dhanhq
import google.generativeai as genai

# --- PAGE SETUP ---
st.set_page_config(page_title="SMC AI Trader", page_icon="📈", layout="centered")
st.title("🤖 SMC Trader - Live Dashboard")

# --- SIDEBAR (LOGIN) ---
with st.sidebar:
    st.subheader("Login Details")
    client_id = st.text_input("Dhan Client ID", value="1109282855")
    access_token = st.text_input("Dhan Access Token", type="password")
    gemini_key = st.text_input("Gemini API Key", type="password")
    
    start_button = st.button("Start System")
    if start_button:
        st.session_state['running'] = True
        st.success("System Live! Data fetching started...")

# --- MAIN LOGIC ---
if 'running' in st.session_state and st.session_state['running']:
    
    # Refresh Button (Manual)
    if st.button("🔄 Refresh Data Now"):
        st.rerun()

    try:
        # 1. API Connections Check
        if not access_token or not gemini_key:
            st.error("⚠️ Please enter Dhan Token and Gemini Key in Sidebar!")
            st.stop()

        dhan = dhanhq(client_id, access_token)
        genai.configure(api_key=gemini_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # --- COLUMNS SETUP ---
        col1, col2 = st.columns(2)

        # 2. FETCH NIFTY DATA (Dhan)
        nifty_price = "N/A"
        with col1:
            try:
                data = dhan.get_ltp_data("NSE_INDEX", "INDEX", 13)
                if data['status'] == 'success':
                    nifty_price = data['data']['last_price']
                    st.metric(label="🇮🇳 NIFTY 50", value=f"₹{nifty_price}")
                else:
                    st.error("Dhan Token Expired?")
            except Exception as e:
                st.error(f"Dhan Error: {e}")

        # 3. FETCH BTC DATA (Binance Public API)
        btc_price = "N/A"
        with col2:
            try:
                url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
                resp = requests.get(url, timeout=5).json()
                btc_price = float(resp['price'])
                st.metric(label="₿ BITCOIN", value=f"${btc_price}")
            except Exception as e:
                st.warning("BTC Data Load Fail")

        # 4. GEMINI ANALYSIS (AI Brain)
        st.write("---")
        st.subheader("🧠 Gemini SMC Analysis")
        
        if nifty_price != "N/A":
            prompt = (f"Act as an SMC Trader. Nifty is {nifty_price}, Bitcoin is {btc_price}. "
                      f"Current Time: {time.strftime('%H:%M')}. "
                      "Is Nifty in Premium or Discount? What is the immediate plan based on 3B'S? "
                      "Keep it very short (2 lines) and Hindi+English mix.")
            
            with st.spinner('AI is thinking...'):
                try:
                    response = model.generate_content(prompt)
                    st.info(f"💡 {response.text}")
                except Exception as e:
                    st.error(f"Gemini Error: {e}")
        else:
            st.warning("Waiting for Nifty Data to start Analysis...")

    except Exception as e:
        st.error(f"Major System Error: {e}")

else:
    st.info("👈 Left Sidebar mein apni Keys daalein aur 'Start System' dabayein.")
