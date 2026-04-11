import streamlit as st
import google.generativeai as genai

# --- 1. إعداد الصفحة (يجب أن يكون أول أمر) ---
st.set_page_config(page_title="Elsewedy Smart Tool", layout="wide")

# --- 2. إعداد الـ API Key ---
part1 = "AIzaSyD2J9a9RXLKjkC-"
part2 = "cw12JR7zxz3t7oVSA-Q"

try:
    genai.configure(api_key=part1 + part2)
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    if available_models:
        selected_model = available_models[0]
        model = genai.GenerativeModel(selected_model)
except Exception as e:
    st.error(f"Configuration Error: {e}")

# --- 3. تنسيق الخلفية والألوان CSS ---
st.markdown("""
    <style>
    .stApp {
        background-color: #FDFDFD; /* أوف وايت */
    }
    h1, h2, h3, p {
        color: #1E1E1E !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. القائمة الجانبية (Sidebar) ---
logo_url = "https://www.elsewedyelectric.com/media/1001/elsewedy-electric-logo.png"
with st.sidebar:
    st.image(logo_url, width=150)
    st.title("Technical Expert")
    st.info("""
    **Eng. Mohamed Tarek** 📞 +966570514091  
    📧 Mohamed.abdelwahab@elsewedy.com
    """)
    st.write("---")
    st.caption("Elsewedy Electric - Smart Solutions")

# --- 5. واجهة الموقع الرئيسية ---
st.image(logo_url, width=200)
st.title("⚡ Elsewedy Electric Smart Tool")
st.markdown(f"**Connected to:** `{selected_model if 'selected_model' in locals() else 'None'}`")
st.markdown("---")

query = st.text_input("Ask a technical question about cables:")

if query:
    with st.spinner("AI is thinking..."):
        try:
            response = model.generate_content(query)
            st.markdown(response.text)
            st.success("Expert Support: Eng. Mohamed Tarek | +966570514091")
        except Exception as e:
            st.error(f"Error: {e}")

# Footer
st.markdown("---")
st.caption("© 2026 Developed by Eng. Mohamed Tarek")
