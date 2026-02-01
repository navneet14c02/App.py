import streamlit as st
import requests
import google.generativeai as genai

st.set_page_config(page_title="Debug Mode", page_icon="🔧")
st.title("🔧 SMC System Debugger")

# --- LOGIN ---
st.sidebar.header("Login")
client_id = st.sidebar.text_input("Client ID", value="1109282855")
access_token = st.sidebar.text_input("New Access Token", type="password")
gemini_key = st.sidebar.text_input("Gemini Key", type="password")

if st.sidebar.button("Test Connection"):
    st.session_state['run'] = True

if 'run' in st.session_state:
    
    # 1. DHAN TEST
    st.subheader("1. Dhan Connection Test")
    
    url = "https://api.dhan.co/v2/marketfeed/ltp"
    
    headers = {
        "access-token": access_token,
        "client-id": client_id,
        "Content-Type": "application/json"
    }
    
    # Nifty 50 Payload
    payload = {
        "exchangeSegment": "NSE_INDEX",
        "instrumentId": "13"
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        
        # --- ASLI ERROR YAHAN DIKHEGA ---
        st.write(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'success':
                price = data['data']['last_price']
                st.success(f"✅ Success! Nifty Price: ₹{price}")
            else:
                st.error(f"❌ Dhan Said No: {data}")
        elif response.status_code == 401:
            st.error("❌ 401 Unauthorized: Aapka TOKEN galat hai ya expire ho gaya hai.")
        else:
            st.error(f"❌ Error Detail: {response.text}")
            
    except Exception as e:
        st.error(f"System Error: {e}")

    # 2. GEMINI TEST
    st.subheader("2. Gemini AI Test")
    if gemini_key:
        try:
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            resp = model.generate_content("Say 'Hello Trader'")
            st.success(f"✅ Gemini is Ready: {resp.text}")
        except Exception as e:
            st.error(f"❌ Gemini Error: {e}")
    else:
        st.warning("Gemini Key nahi daali.")
