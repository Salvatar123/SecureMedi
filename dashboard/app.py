import streamlit as st
import pandas as pd
import sys
import os


# =====================================================
# SHOW REPORT FUNCTION
# =====================================================

def show_report(pid):

    try:
        df = pd.read_csv("logs/data.csv")

        if df.empty:
            st.warning("No health data available yet")
            return

        latest = df.iloc[-1]

        st.divider()
        st.subheader("📊 Patient Health Report")

        col1, col2, col3 = st.columns(3)

        col1.metric("❤️ Heart Rate", latest["heart"])
        col2.metric("🌡 Temperature", latest["temp"])
        col3.metric("🫁 SpO2", latest["spo2"])

        st.subheader("Status")
        st.write(latest["status"])

        st.line_chart(df[["heart", "temp", "spo2"]])

    except Exception as e:
        st.error(f"Could not load report: {e}")


# =====================================================
# IMPORT CONNECTOR
# =====================================================

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from blockchain.connector import (
    verify_key,
    log_access,
    generate_key,
    get_my_key,
    get_access_logs_as_patient,
    generate_emergency,
    is_doctor
)


# =====================================================
# CONFIG
# =====================================================

st.set_page_config(
    page_title="secureMedi Dashboard",
    layout="wide"
)


# =====================================================
# SESSION STATE
# =====================================================

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "emergency" not in st.session_state:
    st.session_state.emergency = False

if "emergency_key" not in st.session_state:
    st.session_state.emergency_key = ""

if "user_address" not in st.session_state:
    st.session_state.user_address = ""

if "patient_id" not in st.session_state:
    st.session_state.patient_id = "P001"


# =====================================================
# SIDEBAR
# =====================================================

st.sidebar.title("🔐 secureMedi Portal")

page = st.sidebar.radio(
    "Navigate",
    ["Login", "Doctor Panel", "Patient Portal"],
    key="main_nav"
)


# =====================================================
# LOGIN PAGE
# =====================================================

if page == "Login":

    if st.session_state.authenticated:
        st.success("Already logged in ✅")
        st.stop()

    st.title("🔐 Secure Login")

    address = st.text_input("Wallet Address")
    key_input = st.text_input("Access Key", type="password")

    if st.button("Login"):

        if address == "" or key_input == "":
            st.warning("Fill all fields")
            st.stop()

        try:
            key_bytes = bytes.fromhex(key_input.replace("0x", ""))

            valid = verify_key(address, key_bytes)

            if valid:

                st.session_state.authenticated = True
                st.session_state.user_address = address

                st.success("Access Granted ✅")
                st.rerun()

            else:
                st.error("Invalid Key ❌")

        except Exception as e:
            st.error(f"Verification Failed: {e}")

    st.stop()


# =====================================================
# BLOCK PATIENT IF NOT LOGGED IN
# =====================================================




# =====================================================
# DOCTOR PANEL
# =====================================================

if page == "Doctor Panel":

    st.title("👨‍⚕️ Doctor Panel")


    # =================================================
    # GENERATE NORMAL KEY
    # =================================================

    st.subheader("🔐 Generate Blockchain Access Key")

    doc_wallet = st.text_input("Doctor Wallet Address")

    if st.button("🔑 Generate New Key"):

        if doc_wallet == "":
            st.error("Enter wallet address")
            st.stop()

        if not is_doctor(doc_wallet):
            st.error("❌ Not a registered doctor")
            st.stop()

        try:
            generate_key()

            key = get_my_key()

            st.success("Key Generated ✅")
            st.code("0x" + key.hex())

        except Exception as e:
            st.error(f"Blockchain Error: {e}")


    st.divider()


    # =================================================
    # EMERGENCY ACCESS
    # =================================================

    st.subheader("🚨 Emergency Access (24 Hours)")

    doc_wallet_em = st.text_input("Doctor Wallet (Emergency)")

    if st.button("🚑 Activate Emergency Mode"):

        if doc_wallet_em == "":
            st.error("Enter wallet address")
            st.stop()

        if not is_doctor(doc_wallet_em):
            st.error("❌ Not a registered doctor")
            st.stop()

        try:
            key = generate_emergency()

            st.session_state.emergency = True
            st.session_state.emergency_key = key

            st.success("Emergency Activated ✅")
            st.code(key)

        except Exception as e:
            st.error(f"Blockchain Error: {e}")


    st.divider()


    # =================================================
    # ACCESS PATIENT RECORD
    # =================================================

    st.subheader("📋 Access Patient Record")


    # ---------- NORMAL MODE ----------

    if st.session_state.authenticated:

        st.success("Verified Doctor Logged In ✅")

        pid = st.text_input("Patient ID")

        if st.button("📂 Access (Normal)"):

            if pid == "":
                st.error("Enter Patient ID")
                st.stop()

            try:
                log_access(pid)

                st.success("Access Granted ✅")

                show_report(pid)

            except Exception as e:
                st.error(e)


    # ---------- EMERGENCY MODE ----------

    elif st.session_state.emergency:

        st.warning("🚨 Emergency Mode Active")

        pid = st.text_input("Patient ID (Emergency)")
        ek = st.text_input("Emergency Key", type="password")

        if st.button("🚨 Emergency Access"):

            if pid == "" or ek == "":
                st.error("Fill all fields")
                st.stop()

            if ek != st.session_state.emergency_key:
                st.error("Invalid Emergency Key ❌")
                st.stop()

            try:
                log_access(pid)

                st.success("Emergency Access Granted ✅")

                show_report(pid)

            except Exception as e:
                st.error(e)


    else:
        st.info("🔒 Login or Emergency Access Required")


# =====================================================
# PATIENT PORTAL
# =====================================================

if page == "Patient Portal":

    st.title("🧑‍⚕️ Patient Portal")

    st.subheader("View My Health Report")

    pid = st.text_input("Patient ID")
    pkey = st.text_input("Private Key", type="password")

    if st.button("📑 View My Report"):

        if pid == "" or pkey == "":
            st.warning("Fill all fields")
            st.stop()

        try:
            doctors, times, emergencies = get_access_logs_as_patient(pid, pkey)

            df = pd.read_csv("logs/data.csv")
            latest = df.iloc[-1]

            st.success("Report Loaded ✅")


            # -------- REPORT --------

            st.divider()
            st.subheader("📊 Latest Vitals")

            col1, col2, col3 = st.columns(3)

            col1.metric("❤️ Heart Rate", latest["heart"])
            col2.metric("🌡 Temperature", latest["temp"])
            col3.metric("🫁 SpO2", latest["spo2"])

            st.subheader("Status")
            st.write(latest["status"])

            st.line_chart(df[["heart", "temp", "spo2"]])


            # -------- LOGS --------

            st.divider()
            st.subheader("🔍 Access History")

            if len(doctors) == 0:

                st.info("No access yet")

            else:

                import datetime

                for i in range(len(doctors)):

                    t = datetime.datetime.fromtimestamp(times[i])

                    mode = "🚨 Emergency" if emergencies[i] else "✅ Normal"

                    st.write(f"""
👨‍⚕️ Doctor: `{doctors[i]}`
⏰ Time: {t}
🩺 Mode: {mode}
---
""")

        except Exception as e:

            st.error(f"Access Denied ❌ : {e}")