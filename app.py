import streamlit as st
import google.generativeai as genai

# --- ضع مفتاحك الجديد هنا ---
part1 = "AIzaSyD2J9a9RXLKjkC-"
part2 = "cw12JR7zxz3t7oVSA-Q"

try:
    genai.configure(api_key=part1 + part2)
    model = genai.GenerativeModel('gemini-1.5-flash')
except:
    st.error("Setup Error")

# --- باقي كود الموقع ---
st.set_page_config(page_title="Elsewedy Smart Tool")
st.title("⚡ Elsewedy Electric Smart Tool")

query = st.text_input("Ask a question:")
if query:
    try:
        response = model.generate_content(query)
        st.write(response.text)
        st.success("Eng. Mohamed Tarek | +966570514091")
    except Exception as e:
        # لو طلعت الرسالة دي تاني، يبقى المفتاح لسه فيه حرف ناقص أو زيادة
        st.error(f"AI Connection Error. Technical details: {e}")
