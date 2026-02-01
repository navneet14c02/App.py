import streamlit as st
import yfinance as yf
import requests
import google.generativeai as genai
import time
from datetime import datetime
import pytz

# --- PAGE CONFIG ---
st.set_page_config(page_title="SMC Auto-Bot", page_icon="🤖", layout="centered")

# Hide Header
st.markdown("""<style>.stAppHeader {display:none;}</style>""", unsafe_allow_html=True)

st.title("🤖 SMC Auto-Pilot (Standard Mode)")
st.caption("🔴 Live Market Monitoring")

# --- SETTINGS ---
with st.sidebar:
    st.header("⚙️ Settings")
    if 'general' in st.secrets:
        gemini_key = st.secrets['general']['gemini_api_key']
        st.success("✅ Gemini Key Found")
    else:
        gemini_key = st.text_input("Gemini API Key", type="password")

    # Index Map
    index_map = {
        "NIFTY 50": "^NSEI",
        "BANK NIFTY": "^NSEBANK",
        "SENSEX": "^BSESN"
    }
    selected_name = st.selectbox("Track Instrument", list(index_map.keys()))
    ticker_symbol = index_map[selected_name]
    
    auto_run = st.checkbox("✅ Enable Auto-Refresh", value=True)

# --- LOGIC ---
price_box = st.empty()
ai_box = st.empty()
timer_box = st.empty()

def get_ist_time():
    IST = pytz.timezone('Asia/Kolkata')
    return datetime.now(IST).strftime('%H:%M:%S')

if gemini_key and auto_run:
    while True:
        try:
            # 1. Fetch Data
            stock = yf.Ticker(ticker_symbol)
            data = stock.history(period="1d", interval="1m")
            
            if not data.empty:
                current_price = round(data['Close'].iloc[-1], 2)
                
                # Fetch BTC
                try:
                    btc_resp = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT", timeout=2).json()
                    btc_price = round(float(btc_resp['price']), 2)
                except:
                    btc_price = "Loading..."

                # Display
                with price_box.container():
                    c1, c2 = st.columns(2)
                    c1.metric(f"🇮🇳 {selected_name}", f"₹{current_price}")
                    c2.metric("₿ BITCOIN", f"${btc_price}")

                # 2. AI ANALYSIS (MODEL NAME CHANGED HERE)
                genai.configure(api_key=gemini_key)
                
                # *** FIX IS HERE: Changed to 'gemini-pro' ***
                model = genai.GenerativeModel('gemini-pro') 
                
                prompt = (
                    f"Time: {get_ist_time()}. {selected_name} is {current_price}. BTC is {btc_price}. "
                    f"As an SMC Trader, give a strict 2-line Action Plan in Hindi. "
                    f"Is it Premium or Discount? Check for Inducement."
                )
                
                with ai_box.container():
                    st.write("---")
                    response = model.generate_content(prompt)
                    st.info(f"💡 **AI PLAN:**\n\n{response.text}")

                # Timer
                for i in range(60, 0, -1):
                    timer_box.caption(f"Refreshing in {i}s...")
                    time.sleep(1)
            
            else:
                st.warning("Market Data Loading...")
                time.sleep(5)

        except Exception as e:
            st.error(f"Error: {e}")
            time.sleep(10)
else:
    st.info("👈 Enter Key & Enable Auto-Refresh")
