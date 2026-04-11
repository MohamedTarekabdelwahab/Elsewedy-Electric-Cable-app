import streamlit as st
import google.generativeai as genai

# --- 1. إعداد الـ API Key ---
# قسم المفتاح الجديد هنا كالعادة
part1 = "AIzaSyD2J9a9RXLKjkC-"
part2 = "cw12JR7zxz3t7oVSA-Q"

try:
    genai.configure(api_key=part1 + part2)
    
    # حركة ذكية: بنجيب لستة الموديلات المتاحة ونختار أول واحد يدعم الشات
    available_models = [m.name for m in genai.list_models() 
                        if 'generateContent' in m.supported_generation_methods]
    
    if available_models:
        # بنختار أول موديل متاح (غالباً هيكون gemini-pro أو gemini-1.5-flash)
        selected_model = available_models[0]
        model = genai.GenerativeModel(selected_model)
    else:
        st.error("No compatible Gemini models found for this API Key.")
except Exception as e:
    st.error(f"Configuration Error: {e}")

# --- 2. واجهة الموقع ---
st.set_page_config(page_title="Elsewedy Smart Tool", layout="wide")
st.title("⚡ Elsewedy Electric Smart Tool")
st.markdown(f"**Connected to:** `{selected_model if 'selected_model' in locals() else 'None'}`")

query = st.text_input("Ask a technical question about cables:")

if query:
    with st.spinner("AI is thinking..."):
        try:
            response = model.generate_content(query)
            st.markdown(response.text)
            st.success("Eng. Mohamed Tarek | +966570514091")
        except Exception as e:
            st.error(f"AI is still sleeping. Error: {e}")

# Footer
st.markdown("---")
st.caption("© 2026 Developed by Eng. Mohamed Tarek")
