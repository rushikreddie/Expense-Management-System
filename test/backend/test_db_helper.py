from backend import db_helper


def test_fetch_expenses_for_date():
    expenses=db_helper.fetch_expenses_for_date('2024-08-05')

    assert len(expenses) == 5
    assert expenses[0]['amount'] == 350
    assert expenses[0]['category'] == "Rent"


def test_fetch_expenses_for_date_invalid():
    expenses = db_helper.fetch_expenses_for_date('2999-08-05')
    assert len(expenses) == 0

def test_fetch_expense_summary_invalid_range():
    summary=db_helper.fetch_expense_summary("2999-08-05","2999-08-09")
    assert len(summary) == 0