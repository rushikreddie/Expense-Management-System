from fastapi import FastAPI, HTTPException
from datetime import date
import db_helper
from typing import List
from pydantic import BaseModel

# Initialize FastAPI application
app = FastAPI()


# ---------------------------------------------------------
# Pydantic Models (Request/Response Schemas)
# ---------------------------------------------------------

class Expense(BaseModel):
    """
    Represents a single expense entry.
    Used for request body validation and response formatting.
    """
    amount: float
    category: str
    notes: str


class DateRange(BaseModel):
    """
    Represents a date range for analytics queries.
    """
    start_date: date
    end_date: date


# ---------------------------------------------------------
# API Endpoints
# ---------------------------------------------------------

@app.get("/expenses/{expense_date}", response_model=List[Expense])
def get_expenses(expense_date: date):
    """
    Retrieve all expenses for a specific date.

    Path Parameter:
        expense_date: Date for which expenses are requested

    Returns:
        List of expense records
    """

    # Fetch data from database
    expenses = db_helper.fetch_expenses_for_date(expense_date)

    # Handle database failure
    if expenses is None:
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve expenses from the database."
        )

    return expenses


@app.post("/expenses/{expense_date}")
def add_or_update_expense(expense_date: date, expenses: List[Expense]):
    """
    Add or update expenses for a specific date.

    Workflow:
    1. Delete existing records for the date
    2. Insert new expense entries
    """

    # Remove existing expenses for the date
    db_helper.delete_expenses_for_date(expense_date)

    # Insert each new expense
    for expense in expenses:
        db_helper.insert_expense(
            expense_date,
            expense.amount,
            expense.category,
            expense.notes
        )

    return {"message": "Expenses updated successfully"}


@app.post("/analytics/")
def analytics(date_range: DateRange):
    """
    Provide category-wise expense analytics for a date range.

    Returns:
        Dictionary containing total amount and percentage per category.
    """

    # Fetch summarized data from database
    data = db_helper.fetch_expense_summary(
        date_range.start_date,
        date_range.end_date
    )

    # Handle database failure
    if data is None:
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve expense summary."
        )

    # Calculate total spending across all categories
    total = sum([row['total'] for row in data])

    breakdown = {}

    # Compute percentage contribution for each category
    for row in data:
        percentage = (row['total'] / total) * 100 if total != 0 else 0

        breakdown[row['category']] = {
            "total": row['total'],
            "percentage": percentage
        }

    return breakdown


@app.post("/analytics_by_month/")
def monthly_analytics(date_range: DateRange):
    """
    Provide month-wise expense totals within a date range.

    Returns:
        Dictionary with month names as keys and total spending as values.
    """

    # Fetch monthly summary from database
    data = db_helper.fetch_monthly_summary(
        date_range.start_date,
        date_range.end_date
    )

    breakdown = {}

    # Build response dictionary
    for row in data:
        breakdown[row["month_name"]] = {
            "total": row["total"]
        }

    return breakdown
