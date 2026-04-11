import streamlit as st
import google.generativeai as genai

# --- 1. الـ API Key الجديد ---
# تأكد إنك حاطط المفتاح الجديد اللي طلعناه من شوية
part1 = "AIzaSyD2J9a9RXLKjkC-"
part2 = "cw12JR7zxz3t7oVSA-Q"

try:
    genai.configure(api_key=part1 + part2)
    # جربنا 'gemini-1.5-flash' بدون إضافات، ده الاسم الرسمي المستقر
    model = genai.GenerativeModel('gemini-1.5-flash')
except:
    st.error("Setup Error")

# --- 2. واجهة الموقع ---
st.set_page_config(page_title="Elsewedy Smart Tool", layout="wide")
st.title("⚡ Elsewedy Electric Smart Tool")
st.markdown("---")

user_query = st.text_input("Ask a technical question about cables:")

if user_query:
    with st.spinner("AI is thinking..."):
        try:
            # هنا بنطلب الرد
            response = model.generate_content(user_query)
            st.markdown(f"**Answer:**\n\n{response.text}")
            st.markdown("---")
            # توقيعك
            st.success("""
            **Contact:** Eng. Mohamed Tarek | +966570514091  
            Mohamed.abdelwahab@elsewedy.com
            """)
        except Exception as e:
            # لو لا قدر الله طلع خطأ تاني، السطر اللي تحت ده هيقولنا الموديلات المتاحة إيه بالظبط
            st.error(f"Try one more time or refresh. Technical error: {e}")
            if "404" in str(e):
                st.warning("Hint: Try changing the model name to 'gemini-pro' in the code.")

# Footer
st.caption("© 2026 Developed by Eng. Mohamed Tarek")
