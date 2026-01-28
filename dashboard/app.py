import streamlit as st
import pandas as pd
import time
import sys
import os

# Add project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from blockchain.connector import get_count

st.set_page_config(page_title="secureMedi Dashboard")

st.title("🏥 secureMedi — Smart Healthcare Monitor")

st.subheader("Real-Time Patient Monitoring")

placeholder = st.empty()

while True:

    try:
        df = pd.read_csv("logs/data.csv")

        latest = df.iloc[-1]

        with placeholder.container():

            col1, col2, col3 = st.columns(3)

            col1.metric("❤️ Heart Rate", latest["heart"])
            col2.metric("🌡 Temperature", latest["temp"])
            col3.metric("🫁 SpO2", latest["spo2"])

            st.write("### Status:", latest["status"])

            st.line_chart(df[["heart", "temp", "spo2"]])

            st.write("🔐 Blockchain Records:", get_count())

    except:
        st.warning("Waiting for sensor data...")

    time.sleep(3)
