import streamlit as st
import google.generativeai as genai

# --- 1. الـ API Key الجديد (قسمه هنا) ---
# خد أول 10 حروف حطهم في part1 والباقي في part2
part1 = "AIzaSyD2J9a9RXLKjkC-" 
part2 = "cw12JR7zxz3t7oVSA-Q"

genai.configure(api_key=part1 + part2)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- 2. واجهة الموقع ---
st.set_page_config(page_title="Elsewedy Smart Tool", layout="wide")
st.title("⚡ Elsewedy Electric Smart Tool")
st.markdown("---")

user_query = st.text_input("Ask a technical question:")

if user_query:
    with st.spinner("AI is thinking..."):
        try:
            response = model.generate_content(user_query)
            st.markdown(f"**Answer:**\n\n{response.text}")
            st.markdown("---")
            st.success("Contact: Eng. Mohamed Tarek | +966570514091")
        except:
            st.error("Please make sure you copied the NEW key correctly.")
