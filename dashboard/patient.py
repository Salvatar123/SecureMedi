import streamlit as st
from blockchain.connector import get_access_logs
import datetime

st.title("🧑‍⚕️ Patient Portal")

wallet = st.text_input("Wallet Address")
pid = st.text_input("Patient ID")

if st.button("View My Report"):

    if wallet == "" or pid == "":
        st.warning("Fill all fields")
        st.stop()

    try:
        doctors, times = get_access_logs(pid)

        if len(doctors) == 0:
            st.info("No access yet")
            st.stop()

        st.success("Access History")

        for i in range(len(doctors)):

            t = datetime.datetime.fromtimestamp(times[i])

            st.write(f"""
Doctor: `{doctors[i]}`
Time: {t}
---
""")

    except:
        st.error("Access Denied ❌")
