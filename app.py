import streamlit as st
import yfinance as yf
import requests
import google.generativeai as genai
from datetime import datetime
import pytz

# --- PAGE CONFIG ---
st.set_page_config(page_title="SMC Sniper Signals", page_icon="🎯", layout="centered")
st.markdown("""<style>.stAppHeader {display:none;}</style>""", unsafe_allow_html=True)

st.title("🎯 SMC Sniper Signals")
st.caption("🔴 Direct Entry/Exit Calls (No Theory)")

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Setup")
    if 'general' in st.secrets:
        gemini_key = st.secrets['general']['gemini_api_key']
    else:
        gemini_key = st.text_input("Gemini API Key", type="password")

    # Mode Selection
    mode = st.radio("Mode:", ["✍️ Manual (Best for Live)", "📡 Auto (Yahoo/Delayed)"])

    # Instrument List
    index_map = {
        "NIFTY 50": "^NSEI",
        "BANK NIFTY": "^NSEBANK",
        "BITCOIN": "BTC-USD",
        "GOLD": "GC=F",
        "RELIANCE": "RELIANCE.NS"
    }
    selected_name = st.selectbox("Instrument", list(index_map.keys()))
    ticker_symbol = index_map[selected_name]

    if st.button("⚡ GENERATE SIGNAL"):
        st.session_state['run'] = True

# --- HELPER ---
def get_valid_model(api_key):
    genai.configure(api_key=api_key)
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                if 'flash' in m.name: return m.name
        return 'gemini-pro'
    except:
        return 'gemini-pro'

# --- MAIN LOGIC ---
if 'run' in st.session_state and st.session_state['run']:
    
    current_price = 0.0
    
    # 1. GET PRICE (Manual or Auto)
    if mode == "✍️ Manual (Best for Live)":
        current_price = st.number_input("🔴 Enter CURRENT LIVE PRICE:", value=0.0, step=0.1)
        if current_price == 0:
            st.warning("Upar Price daalo aur Enter dabao.")
            st.stop()
    else:
        try:
            stock = yf.Ticker(ticker_symbol)
            data = stock.history(period="1d", interval="1m")
            current_price = round(data['Close'].iloc[-1], 2)
            st.info(f"Auto Price (Yahoo): {current_price} (May be delayed)")
        except:
            st.error("Data Error.")
            st.stop()

    # 2. GET BTC CONTEXT
    try:
        btc_resp = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT", timeout=2).json()
        btc_price = round(float(btc_resp['price']), 2)
    except:
        btc_price = "Unknown"

    # 3. GENERATE SIGNAL (New Aggressive Prompt)
    if gemini_key:
        valid_model = get_valid_model(gemini_key)
        genai.configure(api_key=gemini_key)
        model = genai.GenerativeModel(valid_model)
        
        # --- YE HAI ASLI MAGIC (Prompt Change) ---
        prompt = (
            f"Act as a STRICT SMC Signal Provider. No explanations. No theory. "
            f"Instrument: {selected_name}. Current Price: {current_price}. "
            f"Context: Bitcoin Sentiment is {btc_price}. "
            f"Task: Provide a Direct Trade Setup based on probability. "
            f"Output Format (Strictly follow this): "
            f"1. 🚦 SIGNAL: [BUY / SELL / WAIT] "
            f"2. 🎯 ENTRY PRICE: [Exact Number] "
            f"3. 🛑 STOP LOSS: [Exact Number] "
            f"4. 💰 TARGET: [Exact Number] "
            f"5. 📉 REASON: [One very short line, e.g., 'Liquidity swept at low']"
        )
        
        st.write("---")
        with st.spinner("🤖 AI Calculating Entry/Exit..."):
            response = model.generate_content(prompt)
            
            # Result ko bada dikhana
            st.markdown(f"### ⚡ TRADE SETUP for {selected_name}")
            st.success(response.text)
            
            st.caption("Disclaimer: AI prediction. Trade at your own risk.")
            
    else:
        st.error("Key daalo sidebar mein!")
        
