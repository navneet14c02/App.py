import streamlit as st
import yfinance as yf
import requests
import google.generativeai as genai

# --- PAGE CONFIG ---
st.set_page_config(page_title="SMC Free Trader", page_icon="🚀", layout="centered")
st.title("🚀 SMC AI Dashboard (Free Version)")
st.caption("Powered by Yahoo Finance (No Dhan Token Needed)")

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Settings")
    gemini_key = st.text_input("Gemini API Key", type="password")
    
    # Dropdown for Index
    index_map = {
        "NIFTY 50": "^NSEI",
        "BANK NIFTY": "^NSEBANK",
        "SENSEX": "^BSESN"
    }
    selected_index = st.selectbox("Select Index", list(index_map.keys()))
    ticker_symbol = index_map[selected_index]
    
    if st.button("🔴 Start Tracking"):
        st.session_state['run'] = True

# --- MAIN DASHBOARD ---
if 'run' in st.session_state and st.session_state['run']:
    
    if st.button("🔄 Refresh Data"):
        st.rerun()

    # 1. FETCH DATA (YAHOO FINANCE - FREE)
    try:
        col1, col2 = st.columns(2)
        
        # Get Nifty/BankNifty Data
        stock = yf.Ticker(ticker_symbol)
        data = stock.history(period="1d")
        
        if not data.empty:
            current_price = round(data['Close'].iloc[-1], 2)
            
            with col1:
                st.metric(label=f"🇮🇳 {selected_index}", value=f"₹{current_price}")
        else:
            st.error("Market Data Load Fail (Check Internet)")
            current_price = None

        # Get Bitcoin Data (Binance - FREE)
        with col2:
            try:
                btc_url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
                btc_resp = requests.get(btc_url).json()
                btc_price = round(float(btc_resp['price']), 2)
                st.metric(label="₿ BITCOIN", value=f"${btc_price}")
            except:
                btc_price = "Loading..."
                
    except Exception as e:
        st.error(f"Data Error: {e}")

    # 2. GEMINI AI ANALYSIS
    st.write("---")
    st.subheader("🧠 SMC AI Analysis")

    if not gemini_key:
        st.warning("⚠️ Please enter Gemini API Key in Sidebar to get Plan.")
    elif current_price:
        try:
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            prompt = (
                f"Act as an SMC Trader. "
                f"Asset: {selected_index} at Price: {current_price}. "
                f"Global Context: Bitcoin is {btc_price}. "
                f"Task: Based on 3B'S (Bias, Base, Liquidity Sweep), give a short trading plan in Hindi. "
                f"Is the market in Premium or Discount?"
            )
            
            with st.spinner("AI Market Ko Read Kar Raha Hai..."):
                response = model.generate_content(prompt)
                st.success(f"💡 Plan: {response.text}")
                
        except Exception as e:
            st.error(f"Gemini Error: {e}")

else:
    st.info("👈 Sidebar mein Gemini Key daalein aur 'Start' dabayein.")
