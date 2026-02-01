import streamlit as st
import requests
import google.generativeai as genai
import time
from datetime import datetime

# --- PAGE CONFIG ---
st.set_page_config(page_title="SMC Auto-Trader Pro", page_icon="🚀", layout="wide")
st.title("🚀 SMC Auto-Trader Pro - Live SMC Signals")
st.markdown("**Ujjain Trader Special ✨** | Real-time Nifty Analysis")

# --- 1. SAFE AUTO-LOGIN (Secrets ya Manual) ---
auto_login = False
try:
    # Secrets file mile to yeh chalega (Streamlit Cloud ya local .streamlit/secrets.toml)
    if st.secrets["general"]:
        client_id = st.secrets["general"]["dhan_client_id"]
        access_token = st.secrets["general"]["dhan_access_token"]
        gemini_key = st.secrets["general"]["gemini_api_key"]
        auto_login = True
        st.sidebar.success("✅ Auto-Logged in via Secrets!")
except (FileNotFoundError, KeyError):
    st.sidebar.warning("⚠️ Secrets not found → Manual login karo")
    client_id = st.sidebar.text_input("Dhan Client ID", value="1109282855")
    access_token = st.sidebar.text_input("Dhan Access Token", type="password")
    gemini_key = st.sidebar.text_input("Gemini API Key", type="password")

# Sidebar Controls
st.sidebar.markdown("---")
refresh_interval = st.sidebar.slider("Auto Refresh (seconds)", 15, 120, 30)
show_positions = st.sidebar.checkbox("Show Live Positions", value=True)
if st.sidebar.button("🔄 Manual Refresh", use_container_width=True):
    st.rerun()

# Auto-refresh logic
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = 0

time_since = time.time() - st.session_state.last_refresh
if time_since > refresh_interval:
    st.rerun()

# --- 2. VALIDATION ---
if not access_token or not gemini_key:
    st.error("❌ Access Token aur Gemini Key daalo!")
    st.stop()

headers = {
    "access-token": access_token,
    "client-id": client_id,
    "Content-Type": "application/json"
}

# --- LTP Function ---
def get_ltp(exchange_segment, instrument_id):
    url = "https://api.dhan.co/v2/marketfeed/ltp"
    payload = {"exchangeSegment": exchange_segment, "instrumentId": instrument_id}
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if data.get('status') == 'success':
                return data['data']
        elif resp.status_code == 401:
            st.error("❌ Token Expired! Dhan app se naya token generate karo.")
            st.stop()
    except Exception as e:
        st.error(f"Connection Error: {e}")
    return None

# --- Fetch Indices ---
indices = {
    "🇮🇳 NIFTY 50": ("NSE_INDEX", "13"),
    "🏦 BANKNIFTY": ("NSE_INDEX", "260105"),
    "📊 FINNIFTY": ("NSE_INDEX", "260106")
}

prices = {}
for name, (seg, iid) in indices.items():
    data = get_ltp(seg, iid)
    if data:
        prices[name] = {
            "price": data['last_price'],
            "change": data.get('change', 0),
            "pct": data.get('percent_change', 0)
        }

# --- Display Metrics ---
if prices:
    st.markdown("### 📈 Live Market Prices")
    cols = st.columns(len(prices))
    for idx, (name, data) in enumerate(prices.items()):
        with cols[idx]:
            st.metric(
                label=name,
                value=f"₹{data['price']:,.0f}",
                delta=f"{data['change']:+.0f} ({data['pct']:+.2f}%)"
            )
    
    # Update timestamp
    st.session_state.last_refresh = time.time()
    remaining = max(0, refresh_interval - int(time_since))
    st.caption(f"🕐 Last Update: {datetime.now().strftime('%d %b %H:%M:%S')} | Next refresh in {remaining}s")
else:
    st.warning("⚠️ Market data nahi aa raha. Token check karo.")

# --- Gemini SMC Analysis ---
if "🇮🇳 NIFTY 50" in prices:
    nifty_price = prices["🇮🇳 NIFTY 50"]["price"]
    genai.configure(api_key=gemini_key)
    model = genai.GenerativeModel('gemini-1.5-flash')

    prompt = f"""
    Expert SMC Trader ban. Nifty 50: ₹{nifty_price:,}
    Time: {datetime.now().strftime('%H:%M IST')}
    
    Short & clear analysis (4 lines max, Hindi+English):
    1. Premium ya Discount zone?
    2. 3B's status (BOS/CHOCH/FVG)?
    3. Immediate Plan: BUY/SELL/HOLD? Target/SL?
    4. Risk level & reason
    """

    with st.spinner("🧠 AI SMC Signal generate ho raha hai..."):
        try:
            response = model.generate_content(prompt)
            st.markdown("### 🧠 AI SMC Signal")
            st.success(response.text)
        except Exception as e:
            st.error(f"Gemini Error: {e}")
else:
    st.info("Nifty data aane ke baad AI analysis start hoga.")

# --- Live Positions ---
if show_positions:
    st.markdown("---")
    st.subheader("📋 Live Positions")
    try:
        pos_resp = requests.get("https://api.dhan.co/v2/positions", headers=headers, timeout=10).json()
        if pos_resp.get('status') == 'success' and pos_resp.get('data'):
            st.dataframe(pos_resp['data'])
        else:
            st.info("Koi open position nahi hai")
    except:
        st.error("Positions load nahi hue")

# Footer
st.markdown("---")
st.caption("👨‍💻 Navneet (Ujjain) ke liye banaya | Paper trade pehle! | DhanHQ + Gemini Powered 🚀")
