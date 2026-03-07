import streamlit as st
from blockchain.connector import generate_key, get_my_key

st.title("👨‍⚕️ Doctor Panel")

if st.button("Generate Access Key"):

    try:
        generate_key()
        key = get_my_key()

        st.success("Key Generated")
        st.code("0x" + key.hex())

    except Exception as e:
        st.error(e)
