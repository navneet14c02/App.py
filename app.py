import streamlit as st
import yfinance as yf
import requests
import google.generativeai as genai
import time
from datetime import datetime
import pytz

# --- PAGE CONFIG ---
st.set_page_config(page_title="Super SMC Scanner", page_icon="🌍", layout="centered")
st.markdown("""<style>.stAppHeader {display:none;}</style>""", unsafe_allow_html=True)

st.title("🌍 Universal SMC Scanner")
st.caption("Crypto • Forex • Indices • Stocks (Free Data)")

# --- HELPER: AUTO DETECT MODEL (Fix for 404 Error) ---
def get_valid_model(api_key):
    genai.configure(api_key=api_key)
    try:
        # Check list of models
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                if 'flash' in m.name: return m.name
                if 'pro' in m.name: return m.name
        return 'gemini-1.5-flash'
    except:
        return 'gemini-pro'

# --- SIDEBAR SETTINGS ---
with st.sidebar:
    st.header("⚙️ Settings")
    
    # 1. API Key Check
    if 'general' in st.secrets:
        gemini_key = st.secrets['general']['gemini_api_key']
        st.success("✅ Gemini Key Found")
    else:
        gemini_key = st.text_input("Gemini API Key", type="password")

    # 2. THE BIG LIST (Sab kuch yahan hai)
    index_map = {
        "🇮🇳 NIFTY 50": "^NSEI",
        "🇮🇳 BANK NIFTY": "^NSEBANK",
        "🇮🇳 SENSEX": "^BSESN",
        "₿ BITCOIN (24x7)": "BTC-USD",
        "Ξ ETHEREUM": "ETH-USD",
        "🥇 GOLD (Global)": "GC=F",
        "🛢️ CRUDE OIL": "CL=F",
        "💵 USD/INR (Forex)": "INR=X",
        "🏢 RELIANCE IND": "RELIANCE.NS",
        "🏦 HDFC BANK": "HDFCBANK.NS",
        "🚗 TATA MOTORS": "TATAMOTORS.NS"
    }
    
    selected_name = st.selectbox("Select Instrument", list(index_map.keys()))
    ticker_symbol = index_map[selected_name]
    
    auto_run = st.checkbox("✅ Enable Auto-Refresh", value=True)

# --- MAIN DASHBOARD LOGIC ---
price_box = st.empty()
ai_box = st.empty()
timer_box = st.empty()

def get_ist_time():
    IST = pytz.timezone('Asia/Kolkata')
    return datetime.now(IST).strftime('%H:%M:%S')

# System Start
if gemini_key and auto_run:
    
    # Model detect karna (One time)
    valid_model_name = get_valid_model(gemini_key)
    
    while True:
        try:
            # A. FETCH DATA (Yahoo Finance)
            stock = yf.Ticker(ticker_symbol)
            data = stock.history(period="1d", interval="1m") # 1 Minute Data
            
            if not data.empty:
                current_price = round(data['Close'].iloc[-1], 2)
                
                # B. FETCH GLOBAL CONTEXT (BTC)
                try:
                    btc_resp = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT", timeout=2).json()
                    btc_price = round(float(btc_resp['price']), 2)
                except:
                    btc_price = "Loading..."

                # C. DISPLAY PRICE
                with price_box.container():
                    c1, c2 = st.columns(2)
                    c1.metric(f"📈 {selected_name}", f"₹{current_price}")
                    c2.metric("₿ BITCOIN Sentiment", f"${btc_price}")

                # D. AI ANALYSIS
                genai.configure(api_key=gemini_key)
                model = genai.GenerativeModel(valid_model_name)
                
                prompt = (
                    f"Current Time: {get_ist_time()}. "
                    f"Instrument: {selected_name} is trading at {current_price}. "
                    f"Global Context: Bitcoin is {btc_price}. "
                    f"Role: Expert SMC Trader. "
                    f"Task: Analyze market structure (Bias, Inducement, 3B'S). "
                    f"Output: Strict 2-line Action Plan in Hindi. "
                    f"Is it Premium or Discount?"
                )
                
                with ai_box.container():
                    st.write("---")
                    response = model.generate_content(prompt)
                    st.info(f"💡 **AI PLAN ({get_ist_time()}):**\n\n{response.text}")

                # E. COUNTDOWN TIMER
                for i in range(60, 0, -1):
                    timer_box.caption(f"Next Scan in {i} seconds...")
                    time.sleep(1)
            
            else:
                price_box.warning(f"Waiting for Data... ({selected_name} Market Closed?)")
                time.sleep(10)

        except Exception as e:
            st.error(f"Error: {e}")
            time.sleep(10)

else:
    st.info("👈 Sidebar mein Key daalein aur 'Enable' karein.")
