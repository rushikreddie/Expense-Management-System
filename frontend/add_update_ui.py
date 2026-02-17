import streamlit as st
from datetime import datetime
import requests

API_URL = "http://localhost:8000"

def add_update_tab():

    # ---------- HEADER ----------
    st.markdown("""
        <h1 style='text-align:center;'>💰 Daily Expenses</h1>
        <p style='text-align:center; color:gray;'>
            Add or edit your spending for the selected date
        </p>
        <hr>
    """, unsafe_allow_html=True)

    # ---------- DATE PICKER ----------
    selected_date = st.date_input(
        "Select Date",
        datetime(2024, 8, 1),
        label_visibility="collapsed"
    )

    st.markdown(
        f"<h3 style='text-align:center; margin-top:-10px;'>📅 {selected_date.strftime('%d %B %Y')}</h3>",
        unsafe_allow_html=True
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # ---------- FETCH EXISTING ----------
    response = requests.get(f"{API_URL}/expenses/{selected_date}")

    if response.status_code == 200:
        existing_expenses = response.json()
    else:
        st.error("Failed to retrieve expenses")
        existing_expenses = []

    categories = ["Rent", "Food", "Shopping", "Entertainment", "Other"]

    # ---------- FORM ----------
    with st.form(key="expense_form"):

        st.markdown("### 🧾 Expense Entries")

        # Header row
        h1, h2, h3 = st.columns([1, 1, 2])
        h1.markdown("**Amount (₹)**")
        h2.markdown("**Category**")
        h3.markdown("**Notes**")

        st.divider()

        expenses = []

        for i in range(5):

            if i < len(existing_expenses):
                amount = existing_expenses[i]['amount']
                category = existing_expenses[i]["category"]
                notes = existing_expenses[i]["notes"]
            else:
                amount = 0.0
                category = "Shopping"
                notes = ""

            c1, c2, c3 = st.columns([1, 1, 2])

            with c1:
                amount_input = st.number_input(
                    "Amount",
                    min_value=0.0,
                    step=1.0,
                    value=amount,
                    key=f"amount_{i}_{selected_date}",
                    label_visibility="collapsed"
                )

            with c2:
                category_input = st.selectbox(
                    "Category",
                    options=categories,
                    index=categories.index(category),
                    key=f"category_{i}_{selected_date}",
                    label_visibility="collapsed"
                )

            with c3:
                notes_input = st.text_input(
                    "Notes",
                    value=notes,
                    key=f"notes_{i}_{selected_date}",
                    label_visibility="collapsed",
                    placeholder="Optional details..."
                )

            expenses.append({
                'amount': amount_input,
                'category': category_input,
                'notes': notes_input
            })

        st.markdown("<br>", unsafe_allow_html=True)

        # ---------- SUBMIT BUTTON ----------
        submit_button = st.form_submit_button(
            "💾 Save Expenses",
            use_container_width=True
        )

        if submit_button:

            filtered_expenses = [
                e for e in expenses if e['amount'] > 0
            ]

            if not filtered_expenses:
                st.warning("Please enter at least one expense.")
                return

            response = requests.post(
                f"{API_URL}/expenses/{selected_date}",
                json=filtered_expenses
            )

            if response.status_code == 200:
                st.success("Expenses updated successfully ✅")
            else:
                st.error("Failed to update expenses.")
