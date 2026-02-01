import streamlit as st
import time
import requests
import google.generativeai as genai

# --- PAGE CONFIG ---
st.set_page_config(page_title="SMC Pro Trader", page_icon="⚡", layout="centered")
st.title("⚡ SMC Direct Trader")
st.caption("Direct Server Connection • No Library Errors")

# --- FUNCTION: DIRECT API CALL (No Library Needed) ---
def get_dhan_price_direct(client_id, access_token, exchange_seg, security_id):
    try:
        url = "https://api.dhan.co/v2/marketfeed/ltp" # Dhan Server URL
        
        headers = {
            "access-token": access_token,
            "client-id": client_id,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        payload = {
            "exchangeSegment": exchange_seg,
            "instrumentId": str(security_id)
        }
        
        # Direct Request
        response = requests.post(url, headers=headers, json=payload, timeout=5)
        data = response.json()
        
        if data.get('status') == 'success':
            return data['data']['last_price']
        else:
            return None
            
    except Exception as e:
        st.write(f"Debug Info: {e}")
        return None

# --- SIDEBAR: SETTINGS ---
with st.sidebar:
    st.header("🔑 Login")
    client_id = st.text_input("Dhan Client ID", value="1109282855")
    access_token = st.text_input("Dhan Access Token", type="password")
    gemini_key = st.text_input("Gemini API Key", type="password")
    
    st.markdown("---")
    
    # Selection Menu
    script_name = st.selectbox("Select Index:", 
                               ["NIFTY 50", "BANK NIFTY", "FIN NIFTY", "SENSEX"])
    
    # Map Selection to ID
    script_map = {
        "NIFTY 50": {"id": "13", "seg": "NSE_INDEX"},
        "BANK NIFTY": {"id": "25", "seg": "NSE_INDEX"},
        "FIN NIFTY": {"id": "27", "seg": "NSE_INDEX"},
        "SENSEX": {"id": "51", "seg": "BSE_INDEX"},
    }
    
    selected = script_map[script_name]

    if st.button("🚀 Connect Server"):
        st.session_state['running'] = True

# --- MAIN DASHBOARD ---
if 'running' in st.session_state and st.session_state['running']:
    
    if st.button("🔄 Refresh"):
        st.rerun()

    # 1. Credentials Check
    if not access_token or not gemini_key:
        st.error("⚠️ Token aur Key daalna zaroori hai!")
        st.stop()

    # 2. GET PRICE (DIRECT MODE)
    col1, col2 = st.columns(2)
    
    with col1:
        price = get_dhan_price_direct(client_id, access_token, selected['seg'], selected['id'])
        
        if price:
            st.metric(label=f"🇮🇳 {script_name}", value=f"₹{price}")
        else:
            st.error("Data Fetch Fail! Token Check karein.")
            price = "N/A"

    with col2:
        # BTC Data
        try:
            btc_url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
            btc_data = requests.get(btc_url).json()
            btc_price = round(float(btc_data['price']), 2)
            st.metric("₿ BITCOIN", f"${btc_price}")
        except:
            btc_price = "Loading..."

    # 3. GEMINI AI ANALYSIS
    st.write("---")
    st.subheader(f"🧠 SMC AI Logic")
    
    if price != "N/A":
        try:
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            prompt = (
                f"You are a strict SMC Trader. "
                f"Instrument: {script_name} is at {price}. "
                f"Global Context: BTC is {btc_price}. "
                f"Task: Identify if we are in Premium or Discount zone relative to recent range. "
                f"Check for Inducement (IDM) sweep possibilities. "
                f"Give a clear 2-line plan in Hindi."
            )
            
            with st.spinner("Analyzing Market Structure..."):
                response = model.generate_content(prompt)
                st.info(f"💡 {response.text}")
                
        except Exception as e:
            st.error(f"AI Error: {e}")
    else:
        st.warning("Waiting for Price Data...")

else:
    st.info("👈 Login karke 'Connect Server' dabayein.")
