"""Pure calculation and evaluation functions for the learning activity."""

from collections.abc import Iterable, Mapping

from balanced_books.case_data import (
    NOT_ACCOUNTING_TRANSACTION,
    RECORDABLE_TRANSACTIONS,
    STATEMENT_FIELDS,
    TRANSACTIONS,
    Transaction,
)


ASSET_ACCOUNTS = {"Cash", "Accounts Receivable", "Supplies", "Equipment"}
LIABILITY_ACCOUNTS = {"Accounts Payable"}
EQUITY_ACCOUNTS = {"Common Stock"}
REVENUE_ACCOUNTS = {"Service Revenue"}
EXPENSE_ACCOUNTS = {"Rent Expense", "Supplies Expense"}
DIVIDEND_ACCOUNTS = {"Dividends"}


def format_currency(value: int) -> str:
    """Return a whole-dollar amount in student-friendly currency format."""

    return f"${value:,.0f}"


def evaluate_event_type(transaction: Transaction, selected: str) -> dict[str, object]:
    """Evaluate whether a student recognized an event's recording category."""

    return {
        "correct": selected == transaction.event_type,
        "selected": selected,
        "expected": transaction.event_type,
        "explanation": transaction.classification_explanation,
    }


def evaluate_equation_choice(transaction: Transaction, selected: str) -> dict[str, object]:
    """Evaluate a selected dual effect for a recordable transaction."""

    if not transaction.is_recordable:
        raise ValueError("A nonrecordable event has no accounting-equation choice.")

    return {
        "correct": selected == transaction.correct_choice,
        "selected": selected,
        "expected": transaction.correct_choice,
        "explanation": transaction.equation_explanation,
    }


def balances_after(transaction_ids: Iterable[str] | None = None) -> dict[str, int]:
    """Accumulate account balances for the requested recordable transactions."""

    selected_ids = (
        {transaction.id for transaction in RECORDABLE_TRANSACTIONS}
        if transaction_ids is None
        else set(transaction_ids)
    )
    balances: dict[str, int] = {}
    for transaction in TRANSACTIONS:
        if transaction.id not in selected_ids or transaction.event_type == NOT_ACCOUNTING_TRANSACTION:
            continue
        for effect in transaction.effects:
            balances[effect.account] = balances.get(effect.account, 0) + effect.amount
    return balances


def equation_components(balances: Mapping[str, int]) -> dict[str, int]:
    """Translate account balances into the expanded accounting equation."""

    assets = sum(balances.get(account, 0) for account in ASSET_ACCOUNTS)
    liabilities = sum(balances.get(account, 0) for account in LIABILITY_ACCOUNTS)
    contributed_capital = sum(balances.get(account, 0) for account in EQUITY_ACCOUNTS)
    revenue = sum(balances.get(account, 0) for account in REVENUE_ACCOUNTS)
    expenses = sum(balances.get(account, 0) for account in EXPENSE_ACCOUNTS)
    dividends = sum(balances.get(account, 0) for account in DIVIDEND_ACCOUNTS)
    stockholders_equity = contributed_capital + revenue - expenses - dividends
    return {
        "assets": assets,
        "liabilities": liabilities,
        "stockholders_equity": stockholders_equity,
        "liabilities_and_equity": liabilities + stockholders_equity,
    }


def statement_values_from_balances(balances: Mapping[str, int]) -> dict[str, int]:
    """Calculate the company's three financial statements from account balances."""

    service_revenue = balances.get("Service Revenue", 0)
    rent_expense = balances.get("Rent Expense", 0)
    supplies_expense = balances.get("Supplies Expense", 0)
    net_income = service_revenue - rent_expense - supplies_expense
    dividends = balances.get("Dividends", 0)
    ending_retained_earnings = net_income - dividends

    cash = balances.get("Cash", 0)
    accounts_receivable = balances.get("Accounts Receivable", 0)
    supplies = balances.get("Supplies", 0)
    equipment = balances.get("Equipment", 0)
    total_assets = cash + accounts_receivable + supplies + equipment
    accounts_payable = balances.get("Accounts Payable", 0)
    common_stock = balances.get("Common Stock", 0)

    return {
        "service_revenue": service_revenue,
        "rent_expense": rent_expense,
        "supplies_expense": supplies_expense,
        "net_income": net_income,
        "beginning_retained_earnings": 0,
        "re_net_income": net_income,
        "dividends": dividends,
        "ending_retained_earnings": ending_retained_earnings,
        "cash": cash,
        "accounts_receivable": accounts_receivable,
        "supplies": supplies,
        "equipment": equipment,
        "total_assets": total_assets,
        "accounts_payable": accounts_payable,
        "common_stock": common_stock,
        "bs_retained_earnings": ending_retained_earnings,
        "total_liabilities_equity": accounts_payable + common_stock + ending_retained_earnings,
    }


def evaluate_statement_responses(
    responses: Mapping[str, int],
    expected: Mapping[str, int] | None = None,
) -> dict[str, dict[str, int | bool]]:
    """Return item-level correctness for every statement line."""

    expected_values = expected or statement_values_from_balances(balances_after())
    results: dict[str, dict[str, int | bool]] = {}
    for _, key, _, _ in STATEMENT_FIELDS:
        submitted = int(responses.get(key, 0))
        correct_value = int(expected_values[key])
        results[key] = {
            "submitted": submitted,
            "expected": correct_value,
            "correct": submitted == correct_value,
        }
    return results
