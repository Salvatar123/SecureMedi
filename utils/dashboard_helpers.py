"""
Dashboard helper functions.
Shared utilities for the Streamlit dashboard.
"""

import streamlit as st
import pandas as pd
import datetime
import logging
from typing import Optional, List

from config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def show_report(patient_id: Optional[str] = None) -> None:
    """
    Display patient health report from CSV logs.

    Args:
        patient_id: Patient ID (for documentation)
    """
    try:
        df = pd.read_csv(settings.LOG_FILE)

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
        logger.error(f"Failed to load report: {e}")
        st.error(f"Could not load report: {e}")


def display_access_logs(doctors: List[str], times: List[int], emergencies: List[bool]) -> None:
    """
    Display patient access history.

    Args:
        doctors: List of doctor addresses
        times: List of timestamps (unix)
        emergencies: List of emergency flags
    """
    st.divider()
    st.subheader("🔍 Access History")

    if len(doctors) == 0:
        st.info("No access yet")
    else:
        for i in range(len(doctors)):
            t = datetime.datetime.fromtimestamp(times[i])
            mode = "🚨 Emergency" if emergencies[i] else "✅ Normal"

            st.write(f"""
👨‍⚕️ Doctor: `{doctors[i]}`
⏰ Time: {t}
🩺 Mode: {mode}
---
""")
