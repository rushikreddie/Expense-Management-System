import streamlit as st
from datetime import datetime
import requests
import pandas as pd

API_URL = "http://localhost:8000"

def analytics_tab():

    st.set_page_config(layout="centered")

    # ---------- HEADER ----------
    st.markdown("""
        <h1 style='text-align:center;'>📊 Expense Analytics</h1>
        <p style='text-align:center; color:gray;'>
            Understand your spending patterns
        </p>
        <hr>
    """, unsafe_allow_html=True)

    # ---------- DATE RANGE (SIDE BY SIDE) ----------
    col1, col2 = st.columns(2)

    with col1:
        start_date = st.date_input("Start Date", datetime(2024, 8, 1))

    with col2:
        end_date = st.date_input("End Date", datetime(2024, 8, 5))

    st.markdown("<br>", unsafe_allow_html=True)

    # ---------- BUTTON ----------
    if st.button("✨ Generate Analytics", use_container_width=True):

        payload = {
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d")
        }

        response = requests.post(f"{API_URL}/analytics/", json=payload)
        response = response.json()

        # ---------- DATA ----------
        data = {
            "Category": list(response.keys()),
            "Total": [response[c]["total"] for c in response],
            "Percentage": [response[c]["percentage"] for c in response]
        }

        df = pd.DataFrame(data)
        df_sorted = df.sort_values(by="Percentage", ascending=False)

        total_spent = df["Total"].sum()
        top_category = df_sorted.iloc[0]["Category"]
        num_categories = len(df)

        # ---------- SUMMARY ----------
        st.markdown("## 💡 Summary")

        st.metric("💰 Total Spent", f"₹ {total_spent:,.2f}")
        st.metric("🏆 Top Category", top_category)
        st.metric("📂 Categories", num_categories)

        st.divider()

        # ---------- CHART ----------
        st.markdown("## 📈 Spending Distribution")

        st.bar_chart(
            data=df_sorted.set_index("Category")["Percentage"],
            height=450
        )

        st.divider()

        # ---------- TABLE ----------
        st.markdown("## 📋 Detailed Breakdown")

        df_display = df_sorted.copy()
        df_display["Total"] = df_display["Total"].map("₹ {:,.2f}".format)
        df_display["Percentage"] = df_display["Percentage"].map("{:.2f} %".format)

        st.dataframe(
            df_display,
            use_container_width=True,
            hide_index=True
        )

        st.success("Analysis generated successfully ✅")
