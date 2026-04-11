import streamlit as st
import google.generativeai as genai

# 1. Setup Gemini AI
os_api_key = "AIzaSyCkK_ppOOX7_xp-pilsf_nKIagM1nJmzic"
genai.configure(api_key=os_api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

# 2. Page Configuration
st.set_page_config(page_title="Elsewedy Cable Solutions", layout="wide", page_icon="⚡")

# 3. UI Header
st.title("⚡ Professional Cable Selection Suite")
st.subheader("Elsewedy Electric - Engineering Tool")

# 4. Sidebar Resource Center
with st.sidebar:
    st.header("Resource Center")
    try:
        with open("presentation.pptx", "rb") as file:
            st.download_button(
                label="📥 Download Corporate Presentation",
                data=file,
                file_name="Elsewedy_Presentation.pptx",
                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
            )
    except:
        st.warning("Presentation file not found yet.")

# 5. Main Content
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.header("Cable Sizer")
    isc = st.number_input("Short Circuit Current (kA)", value=1.0)
    v_drop = st.number_input("Max Voltage Drop (%)", value=3.0)
    derating = st.slider("Derating Factor", 0.1, 1.0, 0.8)
    
    if st.button("Calculate"):
        # Simple Logic Example
        size = (isc * 1.5) / (v_drop * derating)
        st.success(f"Recommended Size: {size:.2f} mm²")

with col2:
    st.header("AI Technical Support")
    user_query = st.text_input("Ask a technical question:")
    if user_query:
        with st.spinner("Analyzing..."):
            response = model.generate_content(user_query)
            st.markdown(f"**Answer:**\n\n{response.text}")
            st.markdown("---")
            st.info("""
            **For further information please contact:** **Eng. Mohamed Tarek** **Mob no:** +966570514091  
            **Mail:** Mohamed.abdelwahab@elsewedy.com
            """)   





