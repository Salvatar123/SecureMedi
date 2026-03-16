import streamlit as st
import sys
import os
import logging
from typing import Optional, cast

# Configuration and Services
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config.settings import get_settings
from services.blockchain_service import BlockchainService
from services.logger_service import LoggerService
from utils.validators import (
    validate_eth_address,
    validate_patient_id,
    validate_private_key,
)
from utils.dashboard_helpers import show_report, display_access_logs

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
settings = get_settings()

# Initialize services
blockchain_service: Optional[BlockchainService] = None
try:
    blockchain_service = BlockchainService()
except Exception as e:
    logger.warning(f"Blockchain service unavailable: {e}")
    blockchain_service = None

logger_service = LoggerService()


# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(page_title="secureMedi Dashboard", layout="wide")


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
    st.session_state.patient_id = settings.DEFAULT_PATIENT_ID


# =====================================================
# SIDEBAR
# =====================================================

st.sidebar.title("🔐 secureMedi Portal")

page = st.sidebar.radio(
    "Navigate", ["Login", "Doctor Panel", "Patient Portal"], key="main_nav"
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

        if not address or not key_input:
            st.warning("Fill all fields")
            st.stop()

        if not validate_eth_address(address):
            st.error("Invalid wallet address format")
            st.stop()

        if not blockchain_service:
            st.error("Blockchain service unavailable")
            st.stop()

        assert blockchain_service is not None
        try:
            key_bytes = bytes.fromhex(key_input.replace("0x", ""))
            valid = blockchain_service.verify_key(address, key_bytes)

            if valid:
                st.session_state.authenticated = True
                st.session_state.user_address = address
                st.success("Access Granted ✅")
                st.rerun()
            else:
                st.error("Invalid Key ❌")

        except ValueError:
            st.error("Invalid key format")
        except Exception as e:
            st.error(f"Verification Failed: {e}")

    st.stop()


# =====================================================
# DOCTOR PANEL
# =====================================================

if page == "Doctor Panel":

    if not blockchain_service:
        st.error("❌ Blockchain service unavailable")
        st.stop()

    assert blockchain_service is not None

    st.title("👨‍⚕️ Doctor Panel")

    # =================================================
    # GENERATE NORMAL KEY
    # =================================================

    st.subheader("🔐 Generate Blockchain Access Key")

    doc_wallet = st.text_input("Doctor Wallet Address")

    if st.button("🔑 Generate New Key"):

        if not doc_wallet:
            st.error("Enter wallet address")
            st.stop()

        if not validate_eth_address(doc_wallet):
            st.error("Invalid wallet address format")
            st.stop()

        try:
            if not blockchain_service.is_doctor(doc_wallet):
                st.error("❌ Not a registered doctor")
                st.stop()

            blockchain_service.generate_key()
            key = blockchain_service.get_my_key()

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

        if not doc_wallet_em:
            st.error("Enter wallet address")
            st.stop()

        if not validate_eth_address(doc_wallet_em):
            st.error("Invalid wallet address format")
            st.stop()

        try:
            if not blockchain_service.is_doctor(doc_wallet_em):
                st.error("❌ Not a registered doctor")
                st.stop()

            key = blockchain_service.generate_emergency_access()  # type: ignore

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

            if not pid:
                st.error("Enter Patient ID")
                st.stop()

            if not validate_patient_id(pid):
                st.error("Invalid patient ID format (use P001, P002, etc.)")
                st.stop()

            try:
                blockchain_service.log_access(pid)
                st.success("Access Granted ✅")
                show_report(pid)

            except Exception as e:
                st.error(str(e))

    # ---------- EMERGENCY MODE ----------

    elif st.session_state.emergency:

        st.warning("🚨 Emergency Mode Active")

        pid = st.text_input("Patient ID (Emergency)")
        ek = st.text_input("Emergency Key", type="password")

        if st.button("🚨 Emergency Access"):

            if not pid or not ek:
                st.error("Fill all fields")
                st.stop()

            if ek != st.session_state.emergency_key:
                st.error("Invalid Emergency Key ❌")
                st.stop()

            try:
                blockchain_service.log_access(pid)
                st.success("Emergency Access Granted ✅")
                show_report(pid)

            except Exception as e:
                st.error(str(e))

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

        if not pid or not pkey:
            st.warning("Fill all fields")
            st.stop()

        if not validate_patient_id(pid):
            st.error("Invalid patient ID format")
            st.stop()

        if not validate_private_key(pkey):
            st.error("Invalid private key format")
            st.stop()

        if not blockchain_service:
            st.error("Blockchain service unavailable")
            st.stop()

        assert blockchain_service is not None

        try:
            doctors, times, emergencies = blockchain_service.get_access_logs_as_patient(
                pid, pkey
            )

            st.success("Report Loaded ✅")
            show_report(pid)
            display_access_logs(doctors, times, emergencies)

        except Exception as e:
            st.error(f"Access Denied ❌: {e}")