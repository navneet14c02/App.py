import streamlit as st
import requests
import google.generativeai as genai

st.set_page_config(page_title="SMC Auto-Trader", page_icon="🚀", layout="centered")

# --- 1. AUTO-LOGIN MAGIC (SECRETS) ---
# Ye check karega ki kya aapne Settings me keys chhupa rakhi hain?
if 'general' in st.secrets:
    client_id = st.secrets['general']['dhan_client_id']
    access_token = st.secrets['general']['dhan_access_token']
    gemini_key = st.secrets['general']['gemini_api_key']
    auto_login = True
else:
    # Agar secrets nahi mile, toh sidebar me poocho
    st.sidebar.warning("⚠️ Secrets Not Found! Manual Login required.")
    client_id = st.sidebar.text_input("Client ID", value="1109282855")
    access_token = st.sidebar.text_input("Access Token", type="password")
    gemini_key = st.sidebar.text_input("Gemini Key", type="password")
    auto_login = False

# --- 2. MAIN APP ---
st.title("🚀 SMC Auto-Trader")

if st.button("🔄 Check Market Now"):
    
    if not access_token or not gemini_key:
        st.error("❌ Keys Missing! Settings me 'Secrets' add karein.")
        st.stop()

    # --- DHAN DIRECT CALL ---
    try:
        url = "https://api.dhan.co/v2/marketfeed/ltp"
        headers = {
            "access-token": access_token,
            "client-id": client_id,
            "Content-Type": "application/json"
        }
        # Nifty 50 (ID: 13)
        payload = { "exchangeSegment": "NSE_INDEX", "instrumentId": "13" }
        
        resp = requests.post(url, headers=headers, json=payload)
        
        if resp.status_code == 200:
            data = resp.json()
            if data['status'] == 'success':
                price = data['data']['last_price']
                st.metric("🇮🇳 NIFTY 50", f"₹{price}")
                
                # --- GEMINI ANALYSIS ---
                genai.configure(api_key=gemini_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                ai_resp = model.generate_content(f"Nifty is {price}. One line SMC advice?")
                st.info(f"🤖 AI: {ai_resp.text}")
                
            else:
                st.error(f"Dhan Error: {data}")
        elif resp.status_code == 401:
            st.error("❌ Token Expired or Invalid! (Secrets update karein)")
        else:
            st.error(f"Server Error: {resp.status_code}")
            
    except Exception as e:
        st.error(f"Error: {e}")

if auto_login:
    st.caption("✅ Auto-Logged in via Secrets")
