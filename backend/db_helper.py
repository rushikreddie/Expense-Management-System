import mysql.connector
from contextlib import contextmanager
from logging_setup import setup_logger


# Initialize logger for this module
logger = setup_logger('db_helper')


@contextmanager
def get_db_cursor(commit=False):
    """
    Context manager to provide a database cursor.

    Automatically:
    - Opens a database connection
    - Yields a cursor (dictionary format)
    - Commits changes if commit=True
    - Closes cursor and connection after use
    """

    # Establish connection to MySQL database
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Root",
        database="expense_manager"
    )

    # Create cursor that returns rows as dictionaries
    cursor = connection.cursor(dictionary=True)

    # Provide the cursor to the caller
    yield cursor

    # Commit changes only if requested (for INSERT/DELETE/UPDATE)
    if commit:
        connection.commit()

    # Clean up resources
    cursor.close()
    connection.close()


def fetch_expenses_for_date(expense_date):
    """
    Retrieve all expenses for a specific date.
    """

    logger.info(f"fetch_expenses_for_date called with {expense_date}")

    with get_db_cursor() as cursor:
        cursor.execute(
            "SELECT * FROM expenses WHERE expense_date = %s",
            (expense_date,)
        )

        expenses = cursor.fetchall()
        return expenses


def delete_expenses_for_date(expense_date):
    """
    Delete all expense records for a given date.
    """

    logger.info(f"delete_expenses_for_date called with {expense_date}")

    # commit=True ensures the deletion is saved
    with get_db_cursor(commit=True) as cursor:
        cursor.execute(
            "DELETE FROM expenses WHERE expense_date = %s",
            (expense_date,)
        )


def insert_expense(expense_date, amount, category, notes):
    """
    Insert a new expense record into the database.
    """

    logger.info(
        f"insert_expense called with date: {expense_date}, "
        f"amount: {amount}, category: {category}, notes: {notes}"
    )

    # commit=True to persist the inserted data
    with get_db_cursor(commit=True) as cursor:
        cursor.execute(
            """
            INSERT INTO expenses (expense_date, amount, category, notes)
            VALUES (%s, %s, %s, %s)
            """,
            (expense_date, amount, category, notes)
        )


def fetch_expense_summary(start_date, end_date):
    """
    Fetch category-wise expense totals within a date range.
    """

    logger.info(
        f"fetch_expense_summary called with start: {start_date} end: {end_date}"
    )

    with get_db_cursor() as cursor:
        cursor.execute(
            """
            SELECT category, SUM(amount) AS total
            FROM expenses
            WHERE expense_date BETWEEN %s AND %s
            GROUP BY category;
            """,
            (start_date, end_date)
        )

        data = cursor.fetchall()
        return data


def fetch_monthly_summary(start_date, end_date):
    """
    Fetch month-wise expense totals within a date range.
    Returns month number, month name, and total spending.
    """

    query = """
        SELECT 
            MONTH(expense_date) AS month_num,
            MONTHNAME(expense_date) AS month_name,
            SUM(amount) AS total
        FROM expenses
        WHERE expense_date BETWEEN %s AND %s
        GROUP BY month_num, month_name
        ORDER BY month_num
    """

    with get_db_cursor() as cursor:
        cursor.execute(query, (start_date, end_date))
        result = cursor.fetchall()

    return result


# ---------------------------------------------------------
# Local testing block (runs only when file executed directly)
# ---------------------------------------------------------
if __name__ == "__main__":

    # Test: fetch expenses for a specific date
    expenses = fetch_expenses_for_date("2024-09-30")
    print(expenses)

    # Test: fetch category-wise summary
    summary = fetch_expense_summary("2024-08-01", "2024-08-05")
    for record in summary:
        print(record)
