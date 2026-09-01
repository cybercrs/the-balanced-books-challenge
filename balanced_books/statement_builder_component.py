"""Streamlit wrapper for the interactive financial-statement workspace."""

from pathlib import Path
from typing import Any

import streamlit.components.v1 as components


_FRONTEND_DIR = Path(__file__).parent / "statement_builder_frontend"
_statement_builder = components.declare_component(
    "balanced_books_statement_builder",
    path=str(_FRONTEND_DIR),
)
_scroll_to_top = components.declare_component(
    "balanced_books_scroll_to_top",
    path=str(Path(__file__).parent / "scroll_to_top_frontend"),
)


def render_scroll_to_top_component(*, key: str, selector: str | None = None) -> None:
    """Scroll the Streamlit viewport to the top or to a visible page element."""

    _scroll_to_top(selector=selector, key=key, default=None)


def render_statement_builder_component(
    balances: dict[str, int],
    statement_values: dict[str, int],
    *,
    initial_progress: dict[str, Any] | None,
    key: str,
) -> dict[str, Any] | None:
    """Render the drag-and-drop workspace and return progress or completion."""

    account_specs = (
        ("cash", "Cash", "Cash", "asset", 0),
        ("accounts_receivable", "Accounts receivable", "Accounts Receivable", "asset", 0),
        ("supplies", "Supplies", "Supplies", "asset", 0),
        ("equipment", "Equipment", "Equipment", "asset", 0),
        ("accounts_payable", "Accounts payable", "Accounts Payable", "liability", 0),
        ("common_stock", "Common stock", "Common Stock", "equity", 0),
        ("service_revenue", "Service revenue", "Service Revenue", "revenue", 1),
        ("rent_expense", "Rent expense", "Rent Expense", "expense", -1),
        ("supplies_expense", "Supplies expense", "Supplies Expense", "expense", -1),
        ("dividends", "Dividends", "Dividends", "distribution", 0),
    )
    accounts = [
        {
            "id": account_id,
            "label": label,
            "value": balances[balance_key],
            "kind": kind,
            "incomeSign": income_sign,
        }
        for account_id, label, balance_key, kind, income_sign in account_specs
    ]
    derived = [
        {
            "id": "beginning_retained_earnings",
            "label": "Beginning retained earnings",
            "value": statement_values["beginning_retained_earnings"],
            "kind": "derived",
            "incomeSign": 0,
        },
        {
            "id": "net_income",
            "label": "Net income from income statement",
            "value": statement_values["net_income"],
            "kind": "derived",
            "incomeSign": 0,
        },
        {
            "id": "ending_retained_earnings",
            "label": "Ending retained earnings",
            "value": statement_values["ending_retained_earnings"],
            "kind": "derived",
            "incomeSign": 0,
        },
    ]
    return _statement_builder(
        accounts=accounts,
        derived=derived,
        company="Flyer Fuel Coffee Company",
        period="September 30",
        initialProgress=initial_progress,
        key=key,
        default=None,
    )
