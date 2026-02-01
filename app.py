import streamlit as st
import time
import requests
from dhanhq import dhanhq
import google.generativeai as genai

# --- PAGE CONFIG ---
st.set_page_config(page_title="SMC Pro Trader", page_icon="🌍", layout="centered")
st.title("🌍 Universal Scanner")
st.caption("Indices • Stocks • MCX • Forex • Crypto")

# --- SIDEBAR: SETTINGS ---
with st.sidebar:
    st.header("⚙️ Setup")
    # 1. Credentials
    client_id = st.text_input("Dhan Client ID", value="1109282855")
    access_token = st.text_input("Dhan Access Token", type="password")
    gemini_key = st.text_input("Gemini API Key", type="password")
    
    st.markdown("---")
    
    # 2. Instrument Selector (Jadoo Yahan Hai)
    mode = st.radio("Kya Trade Karna Hai?", ["Popular Indices", "Custom (Stocks/MCX)"])
    
    selected_script = None
    exch_type = "NSE_INDEX" # Default
    sec_id = "13"           # Default (Nifty)
    inst_type = "INDEX"     # Default

    if mode == "Popular Indices":
        script_dict = {
            "NIFTY 50": {"id": "13", "exch": "NSE_INDEX", "type": "INDEX"},
            "BANK NIFTY": {"id": "25", "exch": "NSE_INDEX", "type": "INDEX"},
            "FIN NIFTY": {"id": "27", "exch": "NSE_INDEX", "type": "INDEX"},
            "SENSEX": {"id": "51", "exch": "BSE_INDEX", "type": "INDEX"},
        }
        script_name = st.selectbox("Select Index:", list(script_dict.keys()))
        
        # Values set karna
        selected = script_dict[script_name]
        sec_id = selected["id"]
        exch_type = selected["exch"]
        inst_type = selected["type"]
        selected_name = script_name

    else: # Custom Mode (Sabhi ke liye)
        st.info("Kisi bhi Stock/MCX ka Security ID daalein.")
        selected_name = st.text_input("Naam (eg. Crude Oil)", value="Custom Scrip")
        exch_type = st.selectbox("Exchange", ["NSE_EQ", "NSE_FNO", "MCX_COMM", "BSE_EQ"])
        sec_id = st.text_input("Security ID (eg. 11483 for L&T)", value="13")
        inst_type = st.selectbox("Type", ["EQUITY", "INDEX", "FUTCOM", "CURRENCY"])

    # Start Button
    if st.button("🚀 Start Tracking"):
        st.session_state['running'] = True
        st.success(f"Tracking Started: {selected_name}")

# --- MAIN DASHBOARD ---
if 'running' in st.session_state and st.session_state['running']:
    
    # Refresh Button
    if st.button("🔄 Refresh Data"):
        st.rerun()

    try:
        # Check Keys
        if not access_token or not gemini_key:
            st.error("⚠️ Sidebar mein Keys daalna bhool gaye!")
            st.stop()

        # Connect
        dhan = dhanhq(client_id, access_token)
        genai.configure(api_key=gemini_key)
        model = genai.GenerativeModel('gemini-1.5-flash')

        # --- 1. GET DATA FROM DHAN ---
        current_price = "N/A"
        try:
            # Dynamic Data Fetching (Jo aapne select kiya wahi aayega)
            data = dhan.ltp(sec_id, exch_type, inst_type)
            
            if data['status'] == 'success':
                current_price = data['data']['last_price']
                st.metric(label=f"📈 {selected_name}", value=f"₹{current_price}")
            else:
                st.error("❌ Dhan Data Error! Security ID check karein.")
        except Exception as e:
            st.error(f"API Error: {e}")

        # --- 2. GET GLOBAL CONTEXT (Gift Nifty & BTC) ---
        col1, col2 = st.columns(2)
        with col1:
            # Gift Nifty (Yahoo Finance se)
            try:
                gift_url = "https://query1.finance.yahoo.com/v8/finance/chart/INIFTY=F"
                gift_data = requests.get(gift_url, headers={'User-agent': 'Mozilla/5.0'}).json()
                gift_price = gift_data['chart']['result'][0]['meta']['regularMarketPrice']
                st.metric("🌍 Gift Nifty", f"₹{gift_price}")
            except:
                st.caption("Gift Nifty Loading...")
                gift_price = "Unknown"

        with col2:
            # Bitcoin (Binance)
            try:
                btc_url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
                btc_data = requests.get(btc_url).json()
                btc_price = round(float(btc_data['price']), 2)
                st.metric("₿ Bitcoin", f"${btc_price}")
            except:
                btc_price = "Unknown"

        # --- 3. GEMINI AI BRAIN ---
        st.write("---")
        st.subheader(f"🧠 AI Plan for {selected_name}")

        if current_price != "N/A":
            # Prompt ab dynamic hai (Jo select karoge uska naam lega)
            prompt = (
                f"You are an SMC Trading Expert. "
                f"Analyze: {selected_name} is trading at {current_price}. "
                f"Context: Gift Nifty is {gift_price}, Bitcoin is {btc_price}. "
                f"Task: Based on 3B'S (Bias, Base, Liquidity Sweep), give a 2-line trading plan in Hindi. "
                f"Is it in Discount or Premium zone?"
            )
            
            with st.spinner('Analyzing Chart Structure...'):
                response = model.generate_content(prompt)
                st.info(f"💡 {response.text}")
        else:
            st.warning("Data ka wait kar raha hoon...")

    except Exception as e:
        st.error(f"System Error: {e}")

else:
    st.info("👈 Left Sidebar se 'Indices' ya 'Custom Stock' select karein.")
