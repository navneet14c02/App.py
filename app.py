import streamlit as st
import requests

st.set_page_config(page_title="Debug Test", layout="centered")
st.title("🛠️ Dhan Connection Doctor")

# 1. Yahan Token Paste Karein
st.write("Niche apna Naya Token paste karein aur button dabayein:")
user_token = st.text_input("Paste New Access Token Here:", type="password")

if st.button("🔴 Test Connection Now"):
    if not user_token:
        st.error("Pehle Token toh daalo bhai!")
    else:
        # 2. Direct Call to Dhan (No Library)
        url = "https://api.dhan.co/v2/marketfeed/ltp"
        
        headers = {
            "access-token": user_token,
            "client-id": "1109282855", # Aapka ID
            "Content-Type": "application/json"
        }
        
        # Nifty 50 Check
        payload = {
            "exchangeSegment": "NSE_INDEX",
            "instrumentId": "13"
        }
        
        try:
            st.info("Sending Request to Dhan...")
            response = requests.post(url, headers=headers, json=payload)
            
            # 3. RESULT DIKHAO (Raw Sach)
            st.write("---")
            st.subheader("📡 Server Ka Jawab (Raw Response):")
            
            # Server kya bol raha hai, wo as-it-is dikhao
            st.code(response.text)
            
            # Analysis
            if response.status_code == 200:
                data = response.json()
                if data['status'] == 'success':
                    price = data['data']['last_price']
                    st.success(f"✅ PASS! Connection Jud Gaya! Price: {price}")
                    st.balloons()
                else:
                    st.error("❌ FAIL! Token sahi hai par Data nahi mila.")
            elif response.status_code == 401:
                st.error("❌ FAIL (401): Unauthorized. Matlab Token abhi bhi GALAT hai.")
            else:
                st.error(f"❌ FAIL ({response.status_code}): Server Error.")
                
        except Exception as e:
            st.error(f"System Error: {e}")
