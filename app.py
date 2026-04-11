import streamlit as st
import google.generativeai as genai
import os

# 1. إعداد الصفحة (يجب أن يكون أول سطر)
st.set_page_config(page_title="Elsewedy Smart Tool", layout="wide", page_icon="⚡")

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
    .stApp {
        background-color: #F5F5F5; 
    }
    /* توحيد اللون الأسود لكل النصوص */
    .stApp, p, span, h1, h2, h3, h4, label, .stMarkdown, .stTextInput {
        color: #000000 !important;
    }
    /* تنسيق الخطوط */
    * {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    /* تنسيق زر التحميل */
    .stDownloadButton button {
        background-color: #FF0000; /* أحمر السويدي */
        color: white !important;
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# 4. وظيفة عرض اللوجو بأمان
def display_logo(w):
    if os.path.exists("logo.png"):
        st.image("logo.png", width=w)
    else:
        st.warning("Logo (logo.png) not found on GitHub.")

# 5. القائمة الجانبية (Sidebar)
with st.sidebar:
    display_logo(150)
    st.markdown("### 👤 Technical Expert")
    st.markdown("""
    **Eng. Mohamed Tarek** 📞 +966570514091  
    📧 Mohamed.abdelwahab@elsewedy.com
    """)
    
    st.markdown("---")
    st.subheader("📥 Downloads")
    
    # إضافة ملف الـ PDF في السايد بار
    pdf_path = "EE KSA Brochure.pdf"
    if os.path.exists(pdf_path):
        with open(pdf_path, "rb") as f:
            st.download_button(
                label="📄 Download EE KSA Brochure",
                data=f,
                file_name="Elsewedy_KSA_Brochure.pdf",
                mime="application/pdf"
            )
    else:
        st.error("Brochure PDF not found.")

# 6. الواجهة الرئيسية
display_logo(200)
st.title("⚡ Elsewedy Electric Smart Tool")
st.markdown("---")

# خانة السؤال
query = st.text_input("Ask our AI Technical Support about cables:", placeholder="e.g. What is the current carrying capacity of 4x16mm2 PVC cable?")

if query:
    with st.spinner("AI is thinking..."):
        try:
            response = model.generate_content(query)
            # عرض الإجابة
            st.markdown("### 🤖 Answer:")
            st.write(response.text)
            
            # الرسالة الختامية الثابتة بعد كل سؤال
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
st.caption("© 2026 Developed by Eng. Mohamed Tarek | Elsewedy Electric KSA")
