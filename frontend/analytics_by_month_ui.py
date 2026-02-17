import streamlit as st
from datetime import datetime
import requests
import pandas as pd

API_URL = "http://localhost:8000"

def analytics_by_month_tab():

    # ---------- HEADER ----------
    st.markdown("""
        <h1 style='text-align:center;'>📅 Monthly Analytics</h1>
        <p style='text-align:center; color:gray;'>
            Track your spending trends over months
        </p>
        <hr>
    """, unsafe_allow_html=True)

    # ---------- DATE RANGE (SIDE BY SIDE) ----------
    col1, col2 = st.columns(2)

    with col1:
        start_date = st.date_input(
            "Start Date",
            datetime(2024, 8, 1),
            key="month_start_date"
        )

    with col2:
        end_date = st.date_input(
            "End Date",
            datetime(2024, 9, 30),
            key="month_end_date"
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ---------- BUTTON ----------
    if st.button("✨ Generate Monthly Analytics",
                 key="month_button",
                 use_container_width=True):

        if start_date > end_date:
            st.error("Start date cannot be after end date")
            return

        payload = {
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d")
        }

        # ---------- LOADING ----------
        with st.spinner("Analyzing monthly expenses..."):

            try:
                response = requests.post(
                    f"{API_URL}/analytics_by_month/",
                    json=payload
                )
            except Exception as e:
                st.error(f"Connection error: {e}")
                return

        if response.status_code != 200:
            st.error(f"Failed to fetch analytics: {response.status_code}")
            st.write(response.text)
            return

        data = response.json()

        # ---------- VALIDATION ----------
        if not data:
            st.warning("No data found for selected range")
            return

        if isinstance(data, list):
            st.error("Backend returned unexpected format")
            st.write(data)
            return

        df = pd.DataFrame({
            "Month": list(data.keys()),
            "Total": [data[m].get("total", 0) for m in data]
        })

        if df.empty:
            st.warning("No valid monthly totals found")
            return

        total_spent = df["Total"].sum()
        top_month = df.loc[df["Total"].idxmax(), "Month"]
        num_months = len(df)

        # ---------- SUMMARY ----------
        st.markdown("## 💡 Summary")

        st.metric("💰 Total Spent", f"₹ {total_spent:,.2f}")
        st.metric("📈 Highest Spending Month", top_month)
        st.metric("📅 Months Covered", num_months)

        st.divider()

        # ---------- CHART ----------
        st.markdown("## 📊 Monthly Spending Trend")

        st.bar_chart(
            df.set_index("Month")["Total"],
            height=450
        )

        st.divider()

        # ---------- TABLE ----------
        st.markdown("## 📋 Detailed Breakdown")

        df_display = df.copy()
        df_display["Total"] = df_display["Total"].map("₹ {:,.2f}".format)

        st.dataframe(
            df_display,
            use_container_width=True,
            hide_index=True
        )

        st.success("Monthly analysis generated successfully ✅")
