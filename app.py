import streamlit as st
import google.generativeai as genai

# 1. إعداد الصفحة (يجب أن يكون أول سطر)
st.set_page_config(page_title="Elsewedy Smart Tool", layout="wide")

# 2. إعداد الـ API Key (ضع مفتاحك المقسم هنا)
part1 = "AIzaSyD2J9a9RXLKjkC-"
part2 = "cw12JR7zxz3t7oVSA-Q"

try:
    genai.configure(api_key=part1 + part2)
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    if available_models:
        model = genai.GenerativeModel(available_models[0])
except Exception as e:
    st.error(f"Configuration Error: {e}")

# 3. تنسيق الألوان (خلفية أوف وايت وكلام أسود صريح)
st.markdown("""
    <style>
    /* الخلفية أوف وايت */
    .stApp {
        background-color: #F5F5F5; 
    }
    /* جعل كل النصوص سوداء وواضحة جداً */
    .stApp, p, span, h1, h2, h3, label, .stMarkdown {
        color: #000000 !important;
        font-weight: 500;
    }
    /* تنسيق صندوق الإدخال */
    .stTextInput input {
        color: #000000 !important;
        background-color: #FFFFFF !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 4. القائمة الجانبية (Sidebar)
# رابط لوجو بديل ومضمون
logo_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b3/Elsewedy_Electric_Logo.svg/1200px-Elsewedy_Electric_Logo.svg.png"

with st.sidebar:
    st.image(logo_url, width=150)
    st.markdown("### Technical Expert")
    st.markdown("""
    **Eng. Mohamed Tarek** 📞 +966570514091  
    📧 Mohamed.abdelwahab@elsewedy.com
    """)

# 5. الواجهة الرئيسية
st.image(logo_url, width=250)
st.title("⚡ Elsewedy Electric Smart Tool")
st.markdown("---")

query = st.text_input("Ask a technical question about cables:", placeholder="Type your question here...")

if query:
    with st.spinner("AI is thinking..."):
        try:
            response = model.generate_content(query)
            # عرض إجابة الذكاء الاصطناعي
            st.markdown(response.text)
            
            # الرسالة الثابتة المطلوبة بعد كل سؤال
            st.markdown("---")
            st.markdown("#### **For more information Please contact:**")
            st.success("""
            **Eng. Mohamed Tarek** 📞 +966570514091  
            📧 Mohamed.abdelwahab@elsewedy.com
            """)
        except Exception as e:
            st.error(f"Error: {e}")

# Footer
st.markdown("---")
st.caption("© 2026 Developed by Eng. Mohamed Tarek | Elsewedy Electric")
