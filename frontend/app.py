import streamlit as st
from add_update_ui import add_update_tab
from analytics_ui import analytics_tab
from analytics_by_month_ui import analytics_by_month_tab

st.title("Expense Tracker")

tab1, tab2, tab3 = st.tabs([
    "💰 Daily Expenses",
    "📊 Insights",
    "📅 Monthly Trends"
])

with tab1:
    add_update_tab()

with tab2:
    analytics_tab()

with tab3:
    analytics_by_month_tab()

