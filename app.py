import streamlit as st
import google.generativeai as genai

# المفتاح اللي أنت قسمته (تأكد إنه الجديد)
part1 = "AIzaSyD2J9a9RXLKjkC-"
part2 = "cw12JR7zxz3t7oVSA-Q"

try:
    genai.configure(api_key=part1 + part2)
    # التعديل هنا: أضفنا كلمة models/ وكلمة -latest
    model = genai.GenerativeModel('models/gemini-1.5-flash-latest')
except:
    st.error("Setup Error")

# واجهة الموقع
st.set_page_config(page_title="Elsewedy Smart Tool")
st.title("⚡ Elsewedy Electric Smart Tool")

query = st.text_input("Ask a question:")
if query:
    try:
        # محاولة طلب المحتوى
        response = model.generate_content(query)
        st.markdown(response.text)
        st.success("Eng. Mohamed Tarek | +966570514091")
    except Exception as e:
        # لو طلع خطأ 404 تاني، جرب تغير الاسم لـ 'gemini-pro' فقط
        st.error(f"Error: {e}")
