"""Student-facing Streamlit entrypoint for The Balanced Books Challenge."""

from html import escape

import streamlit as st

from balanced_books.case_data import (
    EVENT_TYPE_OPTIONS,
    RECORDABLE_TRANSACTIONS,
    TRANSACTIONS,
)
from balanced_books.engine import (
    balances_after,
    equation_components,
    evaluate_equation_choice,
    evaluate_event_type,
    format_currency,
    statement_values_from_balances,
)
from balanced_books.progress import (
    SNAPSHOT_PARAM,
    activity_defaults,
    reset_saved_progress,
    restore_session_state,
    sync_progress_query,
    validate_component_progress,
)
from balanced_books.statement_builder_component import (
    render_scroll_to_top_component,
    render_statement_builder_component,
)


st.set_page_config(
    page_title="The Balanced Books Challenge",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed",
)


UD_RED = "#CE0037"
UD_BLUE = "#003087"
INK = "#14213D"
MUTED = "#526176"
SURFACE = "#FFFFFF"
BACKGROUND = "#F6F8FB"
SUCCESS = "#137A4B"
WARNING = "#9A5B00"


APP_CSS = f"""
<style>
    :root {{
        --ud-red: {UD_RED};
        --ud-blue: {UD_BLUE};
        --ink: {INK};
        --muted: {MUTED};
        --surface: {SURFACE};
        --background: {BACKGROUND};
        --success: {SUCCESS};
        --warning: {WARNING};
    }}

    .stApp {{ background: var(--background); }}
    [data-testid="stHeaderActionElements"] {{ display: none; }}
    [data-testid="stToolbar"] {{ visibility: hidden; height: 0; }}
    [data-testid="stDecoration"] {{ background: var(--ud-red); }}
    .block-container {{ max-width: 1160px; padding-top: 1.6rem; padding-bottom: 4rem; }}

    h1, h2, h3 {{ color: var(--ink); letter-spacing: -0.02em; }}
    p, li, label {{ color: var(--ink); }}

    .hero {{
        background: linear-gradient(125deg, #00245F 0%, var(--ud-blue) 62%, #164E91 100%);
        border-top: 7px solid var(--ud-red);
        border-radius: 18px;
        padding: 2rem 2.2rem 1.8rem;
        margin-bottom: 1.15rem;
        box-shadow: 0 14px 34px rgba(0, 48, 135, 0.16);
    }}
    .hero-kicker {{
        color: #FFFFFF;
        font-size: 0.82rem;
        font-weight: 800;
        letter-spacing: 0.12em;
        margin-bottom: 0.45rem;
    }}
    .hero h1 {{ color: #FFFFFF; font-size: clamp(2rem, 4vw, 3.3rem); margin: 0; }}
    .hero p {{ color: #EEF4FF; font-size: 1.08rem; margin: 0.7rem 0 0; max-width: 760px; }}

    .stage-row {{
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: 0.45rem;
        margin: 0 0 1.4rem;
    }}
    .stage-pill {{
        background: #E9EDF4;
        border: 1px solid #D6DCE7;
        border-radius: 999px;
        color: #5B6778;
        font-size: 0.78rem;
        font-weight: 700;
        padding: 0.52rem 0.7rem;
        text-align: center;
    }}
    .stage-pill.complete {{ background: #E7F4ED; border-color: #A8D5BE; color: #0A653D; }}
    .stage-pill.active {{ background: var(--ud-red); border-color: var(--ud-red); color: #FFFFFF; }}

    .eyebrow {{ color: var(--ud-red); font-size: 0.78rem; font-weight: 800; letter-spacing: 0.1em; }}
    .lead {{ color: var(--muted); font-size: 1.06rem; max-width: 820px; }}

    .event-card {{
        background: var(--surface);
        border: 1px solid #DCE2EB;
        border-left: 7px solid var(--ud-blue);
        border-radius: 14px;
        padding: 1.2rem 1.35rem;
        margin: 0.7rem 0 1rem;
        box-shadow: 0 8px 22px rgba(20, 33, 61, 0.06);
    }}
    .event-card .document {{ color: var(--ud-blue); font-size: 0.8rem; font-weight: 800; letter-spacing: 0.05em; text-transform: uppercase; }}
    .event-card h3 {{ margin: 0.25rem 0 0.45rem; }}
    .event-card p {{ font-size: 1.05rem; margin: 0; }}

    .concept-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.8rem; margin: 1rem 0 1.4rem; }}
    .concept-card {{ background: #FFFFFF; border: 1px solid #DCE2EB; border-radius: 13px; padding: 1rem; }}
    .concept-number {{ color: var(--ud-red); font-weight: 900; font-size: 1.15rem; }}
    .concept-card strong {{ color: var(--ud-blue); display: block; margin: 0.2rem 0; }}
    .concept-card span {{ color: var(--muted); font-size: 0.92rem; }}

    .equation-anchor {{ scroll-margin-top: 1rem; }}
    .equation-board {{ align-items: stretch; display: grid; grid-template-columns: minmax(0, 1fr) auto minmax(0, 1fr) auto minmax(0, 1fr); gap: 0.5rem; margin: 0.8rem 0 0.65rem; }}
    .equation-component {{ background: #EEF4FF; border: 1px solid #C7D8F4; border-radius: 13px; color: var(--ud-blue); min-width: 0; padding: 0.75rem; text-align: center; }}
    .equation-component-label {{ display: block; font-size: 0.78rem; font-weight: 800; letter-spacing: 0.04em; text-transform: uppercase; }}
    .equation-component-value {{ display: block; font-size: clamp(1.05rem, 2.1vw, 1.35rem); font-variant-numeric: tabular-nums; font-weight: 900; margin-top: 0.12rem; }}
    .equation-operator {{ align-self: start; color: var(--ud-blue); font-size: 1.5rem; font-weight: 900; padding-top: 1.05rem; }}
    .equation-component-changes {{ display: grid; gap: 0.35rem; margin-top: 0.55rem; }}
    .equation-change-pill {{ border: 1px solid; border-radius: 9px; font-size: 0.76rem; font-weight: 800; line-height: 1.25; padding: 0.4rem 0.45rem; }}
    .equation-change-pill.increase {{ background: #E7F4ED; border-color: #A8D5BE; color: #0A653D; }}
    .equation-change-pill.decrease {{ background: #FFF0F1; border-color: #E7ABB7; color: #A32638; }}
    .equation-change-pill .direction {{ font-size: 1rem; margin-right: 0.2rem; }}

    .feedback-row {{
        align-items: flex-start;
        background: #FFFFFF;
        border: 1px solid #DCE2EB;
        border-radius: 10px;
        display: flex;
        gap: 1rem;
        justify-content: space-between;
        margin: 0.42rem 0;
        padding: 0.72rem 0.85rem;
    }}
    .feedback-row.correct {{ border-left: 5px solid var(--success); }}
    .feedback-row.review {{ border-left: 5px solid var(--warning); }}
    .feedback-label {{ font-weight: 760; }}
    .feedback-detail {{ color: var(--muted); font-size: 0.9rem; margin-top: 0.12rem; }}
    .feedback-value {{ color: var(--ink); font-variant-numeric: tabular-nums; white-space: nowrap; }}

    .statement {{ background: #FFFFFF; border: 1px solid #DCE2EB; border-radius: 13px; padding: 1rem 1.05rem; }}
    .statement-title {{ color: var(--ud-blue); font-size: 1.05rem; font-weight: 850; margin-bottom: 0.1rem; text-align: center; }}
    .statement-period {{ color: var(--muted); font-size: 0.82rem; margin-bottom: 0.7rem; text-align: center; }}
    .statement-line {{ display: flex; gap: 0.8rem; justify-content: space-between; padding: 0.3rem 0; }}
    .statement-line.indent {{ padding-left: 1rem; }}
    .statement-line.total {{ border-top: 1px solid #7C8799; font-weight: 800; margin-top: 0.2rem; padding-top: 0.45rem; }}
    .statement-line.grand-total {{ border-bottom: 3px double var(--ink); border-top: 1px solid var(--ink); font-weight: 850; margin-top: 0.25rem; padding: 0.45rem 0 0.35rem; }}
    .statement-section {{ color: var(--ud-red); font-size: 0.82rem; font-weight: 850; letter-spacing: 0.05em; margin-top: 0.55rem; text-transform: uppercase; }}
    .amount {{ font-variant-numeric: tabular-nums; white-space: nowrap; }}

    .flow-note {{
        background: #FFF5F7;
        border-left: 5px solid var(--ud-red);
        border-radius: 10px;
        color: var(--ink);
        margin: 0.55rem 0;
        padding: 0.8rem 0.9rem;
    }}
    .score-box {{
        background: linear-gradient(135deg, #FFFFFF 0%, #F2F6FC 100%);
        border: 1px solid #DCE2EB;
        border-radius: 14px;
        padding: 1rem 1.1rem;
        text-align: center;
    }}
    .score-box strong {{ color: var(--ud-blue); display: block; font-size: 1.65rem; }}
    .score-box span {{ color: var(--muted); font-size: 0.87rem; }}

    .stButton > button, .stFormSubmitButton > button {{ border-radius: 9px; font-weight: 760; min-height: 2.7rem; }}
    .stButton > button[kind="primary"], .stFormSubmitButton > button[kind="primary"] {{ background: var(--ud-red); border-color: var(--ud-red); color: #FFFFFF; }}
    .stButton > button[kind="primary"]:hover, .stFormSubmitButton > button[kind="primary"]:hover {{ background: #A9002E; border-color: #A9002E; color: #FFFFFF; }}
    .stButton > button[kind="secondary"] {{ background: #FFFFFF; border-color: #AAB4C5; color: var(--ink); }}

    @media (max-width: 760px) {{
        .block-container {{ padding-left: 1rem; padding-right: 1rem; }}
        .hero {{ padding: 1.45rem 1.25rem; }}
        .stage-row {{ grid-template-columns: 1fr; gap: 0.25rem; }}
        .stage-pill {{ display: none; }}
        .stage-pill.active {{ display: block; }}
        .concept-grid {{ grid-template-columns: 1fr; }}
        .equation-board {{ grid-template-columns: 1fr; }}
        .equation-operator {{ display: none; }}
        .feedback-row {{ display: block; }}
        .feedback-value {{ display: block; margin-top: 0.35rem; }}
    }}
</style>
"""


STAGE_LABELS = ("Welcome", "Transaction Inbox", "Equation Lab", "Statement Builder", "Debrief")


def initialize_state() -> None:
    if "bbc_restore_attempted" not in st.session_state:
        restore_session_state(st.session_state, st.query_params.get(SNAPSHOT_PARAM))
        st.session_state.bbc_restore_attempted = True
    for key, value in activity_defaults().items():
        if key not in st.session_state:
            st.session_state[key] = value


def restart_activity() -> None:
    reset_saved_progress(st.session_state, st.query_params)


def set_stage(stage: int) -> None:
    st.session_state.bbc_stage = stage
    st.session_state.bbc_inbox_warning = None
    st.session_state.bbc_equation_warning = None
    st.session_state.bbc_scroll_token += 1


def submit_inbox_answer(transaction_id: str) -> None:
    transaction = next(item for item in TRANSACTIONS if item.id == transaction_id)
    selected = st.session_state.get(f"inbox_choice_{transaction_id}")
    if selected is None:
        st.session_state.bbc_inbox_warning = transaction_id
        return
    st.session_state.bbc_inbox_warning = None
    st.session_state.bbc_inbox_responses[transaction_id] = selected
    st.session_state.bbc_inbox_feedback[transaction_id] = evaluate_event_type(transaction, selected)


def advance_inbox() -> None:
    if st.session_state.bbc_inbox_index == len(TRANSACTIONS) - 1:
        set_stage(2)
    else:
        st.session_state.bbc_inbox_index += 1
        st.session_state.bbc_inbox_warning = None


def submit_equation_answer(transaction_id: str) -> None:
    transaction = next(item for item in RECORDABLE_TRANSACTIONS if item.id == transaction_id)
    selected = st.session_state.get(f"equation_choice_{transaction_id}")
    if selected is None:
        st.session_state.bbc_equation_warning = transaction_id
        return
    st.session_state.bbc_equation_warning = None
    st.session_state.bbc_equation_responses[transaction_id] = selected
    st.session_state.bbc_equation_feedback[transaction_id] = evaluate_equation_choice(transaction, selected)


def advance_equation() -> None:
    if st.session_state.bbc_equation_index == len(RECORDABLE_TRANSACTIONS) - 1:
        set_stage(3)
    else:
        st.session_state.bbc_equation_index += 1
        st.session_state.bbc_equation_warning = None


def apply_pending_scroll_reset() -> None:
    """Return the main Streamlit viewport to the top after a stage change."""

    if st.session_state.bbc_scroll_applied == st.session_state.bbc_scroll_token:
        return
    render_scroll_to_top_component(key=f"scroll_to_top_{st.session_state.bbc_scroll_token}")
    st.session_state.bbc_scroll_applied = st.session_state.bbc_scroll_token


def render_header() -> None:
    st.markdown(APP_CSS, unsafe_allow_html=True)
    st.markdown(
        """
        <div class="hero">
            <div class="hero-kicker">INTERACTIVE ACCOUNTING SIMULATION</div>
            <h1>The Balanced Books Challenge</h1>
            <p>Follow one business from everyday economic events to a balanced set of financial statements.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_stage_row() -> None:
    active = st.session_state.bbc_stage
    pills = []
    for index, label in enumerate(STAGE_LABELS):
        state_class = "active" if index == active else "complete" if index < active else ""
        status = "Current: " if index == active else "Completed: " if index < active else "Upcoming: "
        pills.append(
            f'<div class="stage-pill {state_class}" aria-label="{status}{escape(label)}">{escape(label)}</div>'
        )
    st.markdown(f'<div class="stage-row">{"".join(pills)}</div>', unsafe_allow_html=True)
    if 0 < active < len(STAGE_LABELS) - 1:
        _, action_column = st.columns([5, 1])
        action_column.button(
            "Start over",
            key="bbc_main_start_over",
            use_container_width=True,
            on_click=restart_activity,
        )


def render_sidebar() -> None:
    with st.sidebar:
        st.header("Activity guide")
        st.write("Complete the rounds in order. Progress is saved in this page's URL so a refresh can recover it. The saved progress contains no identifying information and is not submitted.")
        st.markdown("**Accounting equation**")
        st.code("Assets = Liabilities + Stockholders' Equity", language=None)


def render_event_card(transaction) -> None:
    st.markdown(
        f"""
        <div class="event-card">
            <div class="document">Source: {escape(transaction.document)}</div>
            <h3>{escape(transaction.title)}</h3>
            <p>{escape(transaction.event)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_choice_feedback(feedback: dict[str, object]) -> None:
    selected = str(feedback["selected"]).replace("$", r"\$")
    expected = str(feedback["expected"]).replace("$", r"\$")
    if feedback["correct"]:
        st.success(f"Correct — {expected}")
    else:
        st.error(f"Review this one. You selected: {selected}")
        st.info(f"Correct response: {expected}")
    st.write(feedback["explanation"])


def score_count(responses: dict[str, str], items, answer_attribute: str) -> tuple[int, int]:
    correct = sum(
        responses.get(item.id) == getattr(item, answer_attribute)
        for item in items
    )
    return correct, len(items)


def render_welcome() -> None:
    st.markdown('<div class="eyebrow">YOUR ROLE</div>', unsafe_allow_html=True)
    st.header("Help Flyer Fuel Coffee Company complete its first month")
    st.markdown(
        '<p class="lead">You are the company\'s accounting team. Decide which events belong in the accounting system, analyze each transaction\'s dual effect, and use the resulting balances to prepare the financial statements.</p>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="concept-grid">
            <div class="concept-card"><div class="concept-number">01</div><strong>Collect</strong><span>Recognize the economic events that require recording.</span></div>
            <div class="concept-card"><div class="concept-number">02</div><strong>Process</strong><span>Identify how each transaction changes the accounting equation.</span></div>
            <div class="concept-card"><div class="concept-number">03</div><strong>Communicate</strong><span>Turn account balances into useful financial statements.</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        st.subheader("What to watch for")
        st.markdown(
            """
            - **On account** does not automatically mean cash changed.
            - **Supplies** remain an asset until they are used.
            - **Cash distributions to owners** are accounting transactions, but they are not expenses and do not affect net income.
            - A balanced equation can still contain the wrong accounts—think about the business meaning.
            """
        )

    st.button(
        "Begin the challenge",
        type="primary",
        use_container_width=True,
        on_click=set_stage,
        args=(1,),
    )


def render_transaction_inbox() -> None:
    index = st.session_state.bbc_inbox_index
    transaction = TRANSACTIONS[index]
    feedback = st.session_state.bbc_inbox_feedback.get(transaction.id)
    completed = index + (1 if feedback else 0)

    st.markdown('<div class="eyebrow">ROUND 1 · COLLECT</div>', unsafe_allow_html=True)
    st.header("Transaction Inbox")
    st.write("Decide whether each event changes an account and should enter the accounting records now.")
    st.progress(completed / len(TRANSACTIONS), text=f"Event {index + 1} of {len(TRANSACTIONS)}")
    render_event_card(transaction)

    if feedback is None:
        st.radio(
            "Is this an accounting transaction?",
            EVENT_TYPE_OPTIONS,
            index=None,
            key=f"inbox_choice_{transaction.id}",
        )
        st.button(
            "Check this event",
            type="primary",
            use_container_width=True,
            on_click=submit_inbox_answer,
            args=(transaction.id,),
        )
        if st.session_state.bbc_inbox_warning == transaction.id:
            st.warning("Choose a classification before checking the event.")
    else:
        render_choice_feedback(feedback)
        is_last = index == len(TRANSACTIONS) - 1
        next_label = "Continue to the Equation Lab" if is_last else "Next event"
        st.button(
            next_label,
            type="primary",
            use_container_width=True,
            on_click=advance_inbox,
        )


def render_equation_snapshot(completed_count: int, changed_transaction=None) -> None:
    completed_ids = [transaction.id for transaction in RECORDABLE_TRANSACTIONS[:completed_count]]
    balances = balances_after(completed_ids)
    equation = equation_components(balances)
    change_groups = {"assets": [], "liabilities": [], "equity": []}
    account_components = {
        "Cash": "assets",
        "Accounts Receivable": "assets",
        "Supplies": "assets",
        "Equipment": "assets",
        "Accounts Payable": "liabilities",
        "Common Stock": "equity",
        "Service Revenue": "equity",
        "Rent Expense": "equity",
        "Supplies Expense": "equity",
        "Dividends": "equity",
    }
    if changed_transaction is not None:
        for effect in changed_transaction.effects:
            increase = effect.amount > 0
            direction = "increase" if increase else "decrease"
            arrow = "↑" if increase else "↓"
            word = "increases" if increase else "decreases"
            pill = (
                f'<div class="equation-change-pill {direction}" aria-label="{escape(effect.account)} {word} {format_currency(abs(effect.amount))}">'
                f'<span class="direction">{arrow}</span>{escape(effect.account)} {word} {format_currency(abs(effect.amount))}</div>'
            )
            change_groups[account_components[effect.account]].append(pill)

    def equation_component(label: str, value: int, component: str) -> str:
        changes = "".join(change_groups[component])
        changes_html = (
            f'<div class="equation-component-changes" aria-label="{escape(label)} changes">{changes}</div>'
            if changes
            else ""
        )
        return (
            f'<section class="equation-component {component}">'
            f'<span class="equation-component-label">{escape(label)}</span>'
            f'<span class="equation-component-value">{format_currency(value)}</span>'
            f'{changes_html}</section>'
        )

    st.markdown(
        f"""
        <div class="equation-anchor">
            <div class="equation-board" aria-label="Accounting equation">
                {equation_component("Assets", equation["assets"], "assets")}
                <div class="equation-operator" aria-hidden="true">=</div>
                {equation_component("Liabilities", equation["liabilities"], "liabilities")}
                <div class="equation-operator" aria-hidden="true">+</div>
                {equation_component("Stockholders' Equity", equation["stockholders_equity"], "equity")}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_equation_lab() -> None:
    index = st.session_state.bbc_equation_index
    transaction = RECORDABLE_TRANSACTIONS[index]
    feedback = st.session_state.bbc_equation_feedback.get(transaction.id)
    completed = index + (1 if feedback else 0)

    st.markdown('<div class="eyebrow">ROUND 2 · PROCESS</div>', unsafe_allow_html=True)
    st.header("Equation Lab")
    st.write("Choose the dual effect that correctly represents each recordable transaction.")
    st.progress(completed / len(RECORDABLE_TRANSACTIONS), text=f"Transaction {index + 1} of {len(RECORDABLE_TRANSACTIONS)}")
    render_event_card(transaction)

    if feedback is None:
        st.radio(
            "Which account effects are correct?",
            transaction.choices,
            index=None,
            key=f"equation_choice_{transaction.id}",
            format_func=lambda choice: choice.replace("$", r"\$"),
        )
        render_equation_snapshot(completed)
        st.button(
            "Check the dual effect",
            type="primary",
            use_container_width=True,
            on_click=submit_equation_answer,
            args=(transaction.id,),
        )
        if st.session_state.bbc_equation_warning == transaction.id:
            st.warning("Choose an account effect before checking the transaction.")
    else:
        render_choice_feedback(feedback)
        if not feedback["correct"]:
            st.caption("The equation display uses the corrected transaction so the business can continue with accurate balances.")
        render_equation_snapshot(completed, transaction)
        render_scroll_to_top_component(
            key=f"scroll_equation_{transaction.id}",
            selector=".equation-anchor",
        )
        is_last = index == len(RECORDABLE_TRANSACTIONS) - 1
        next_label = "Build the financial statements" if is_last else "Next transaction"
        st.button(
            next_label,
            type="primary",
            use_container_width=True,
            on_click=advance_equation,
        )


def render_statement_builder() -> None:
    st.markdown('<div class="eyebrow">ROUND 3 · COMMUNICATE</div>', unsafe_allow_html=True)
    st.header("Statement Builder")
    st.write("Build each statement from the correct account balances. Place balances into the labeled sections and watch the statement totals update immediately.")
    st.info("On a computer, drag balances into place. You can also select a balance and choose “Place selected here,” which works with keyboards and touch devices.")

    result = render_statement_builder_component(
        balances_after(),
        statement_values_from_balances(balances_after()),
        initial_progress=st.session_state.bbc_statement_progress,
        key="statement_builder_workspace_v7",
    )
    if result:
        progress = validate_component_progress(result.get("progress"))
        if progress is not None:
            st.session_state.bbc_statement_progress = progress
        if result.get("completed") and progress is not None:
            st.session_state.bbc_statement_completion = {
                "completed": True,
                "statementsFinalized": result.get("statementsFinalized"),
                "attempts": result.get("attempts"),
            }
            set_stage(4)
            sync_progress_query(st.session_state, st.query_params)
            # The component value arrives after this page was selected for rendering.
            st.rerun()


def statement_html(title: str, period: str, lines: list[tuple[str, int | None, str]]) -> str:
    rendered_lines = []
    for label, value, style in lines:
        if style == "section":
            rendered_lines.append(f'<div class="statement-section">{escape(label)}</div>')
            continue
        amount = "" if value is None else format_currency(value)
        rendered_lines.append(
            f'<div class="statement-line {style}"><span>{escape(label)}</span><span class="amount">{amount}</span></div>'
        )
    return (
        '<div class="statement">'
        f'<div class="statement-title">{escape(title)}</div>'
        f'<div class="statement-period">{escape(period)}</div>'
        f'{"".join(rendered_lines)}'
        '</div>'
    )


def render_completed_statements() -> None:
    values = statement_values_from_balances(balances_after())
    selected = st.radio(
        "Choose a finalized financial statement",
        ["Income Statement", "Retained Earnings Statement", "Classified Balance Sheet"],
        horizontal=True,
        label_visibility="collapsed",
        key="bbc_review_statement",
    )
    if selected == "Income Statement":
        st.markdown(
            statement_html(
                "Flyer Fuel Coffee Company · Multi-Step Income Statement",
                "For the Month Ended September 30",
                [
                    ("Operating revenue", None, "section"),
                    ("Service revenue", values["service_revenue"], "indent"),
                    ("Total operating revenue", values["service_revenue"], "total"),
                    ("Operating expenses", None, "section"),
                    ("Rent expense", values["rent_expense"], "indent"),
                    ("Supplies expense", values["supplies_expense"], "indent"),
                    ("Total operating expenses", values["rent_expense"] + values["supplies_expense"], "total"),
                    ("Income from operations", values["net_income"], "total"),
                    ("Other revenues and expenses", None, "section"),
                    ("None in this case", 0, "indent"),
                    ("Net income", values["net_income"], "grand-total"),
                ],
            ),
            unsafe_allow_html=True,
        )
    elif selected == "Retained Earnings Statement":
        st.markdown(
            statement_html(
                "Flyer Fuel Coffee Company · Retained Earnings Statement",
                "For the Month Ended September 30",
                [
                    ("Beginning retained earnings", values["beginning_retained_earnings"], ""),
                    ("Add: Net income", values["re_net_income"], ""),
                    ("Less: Dividends", values["dividends"], ""),
                    ("Ending retained earnings", values["ending_retained_earnings"], "grand-total"),
                ],
            ),
            unsafe_allow_html=True,
        )
    else:
        total_current_assets = values["cash"] + values["accounts_receivable"] + values["supplies"]
        total_equity = values["common_stock"] + values["bs_retained_earnings"]
        st.markdown(
            statement_html(
                "Flyer Fuel Coffee Company · Classified Balance Sheet",
                "September 30",
                [
                    ("Assets", None, "section"),
                    ("Current assets", None, "section"),
                    ("Cash", values["cash"], "indent"),
                    ("Accounts receivable", values["accounts_receivable"], "indent"),
                    ("Supplies", values["supplies"], "indent"),
                    ("Total current assets", total_current_assets, "total"),
                    ("Long-term investments", None, "section"),
                    ("None in this case", 0, "indent"),
                    ("Property, plant, and equipment", None, "section"),
                    ("Equipment", values["equipment"], "indent"),
                    ("Total property, plant, and equipment", values["equipment"], "total"),
                    ("Intangible assets", None, "section"),
                    ("None in this case", 0, "indent"),
                    ("Total assets", values["total_assets"], "grand-total"),
                    ("Liabilities", None, "section"),
                    ("Current liabilities", None, "section"),
                    ("Accounts payable", values["accounts_payable"], "indent"),
                    ("Total current liabilities", values["accounts_payable"], "total"),
                    ("Long-term liabilities", None, "section"),
                    ("None in this case", 0, "indent"),
                    ("Total liabilities", values["accounts_payable"], "total"),
                    ("Stockholders' equity", None, "section"),
                    ("Common stock", values["common_stock"], "indent"),
                    ("Retained earnings", values["bs_retained_earnings"], "indent"),
                    ("Total stockholders' equity", total_equity, "total"),
                    ("Total liabilities and stockholders' equity", values["total_liabilities_equity"], "grand-total"),
                ],
            ),
            unsafe_allow_html=True,
        )


def render_debrief() -> None:
    st.markdown('<div class="eyebrow">CHALLENGE COMPLETE</div>', unsafe_allow_html=True)
    st.header("From events to useful information")
    st.write("The accounting information system collected the source events, processed their effects, and communicated the results through financial statements.")

    inbox_correct, inbox_total = score_count(st.session_state.bbc_inbox_responses, TRANSACTIONS, "event_type")
    equation_correct, equation_total = score_count(
        st.session_state.bbc_equation_responses, RECORDABLE_TRANSACTIONS, "correct_choice"
    )
    statement_completion = st.session_state.bbc_statement_completion or {}
    statement_correct = int(statement_completion.get("statementsFinalized", 0))
    statement_total = 3

    columns = st.columns(3)
    score_data = (
        ("Transaction recognition", inbox_correct, inbox_total),
        ("Dual-effect analysis", equation_correct, equation_total),
        ("Finalized statements", statement_correct, statement_total),
    )
    for column, (label, correct, total) in zip(columns, score_data):
        column.markdown(
            f'<div class="score-box"><strong>{correct}/{total}</strong><span>{escape(label)}</span></div>',
            unsafe_allow_html=True,
        )

    st.subheader("The completed statements")
    render_completed_statements()

    st.subheader("Follow the information flow")
    st.markdown(
        """
        <div class="flow-note"><strong>Revenue and expenses → Net income.</strong> Service revenue of $4,300 minus $1,400 of expenses produced $2,900 of net income.</div>
        <div class="flow-note"><strong>Net income and owner distributions → Retained earnings.</strong> Net income increased retained earnings, while the $600 distribution reduced it. The cash distribution was an accounting transaction, but it was not an expense.</div>
        <div class="flow-note"><strong>Ending retained earnings → Balance sheet.</strong> Ending retained earnings of $2,300 helped stockholders' equity balance total assets of $22,800.</div>
        """,
        unsafe_allow_html=True,
    )

    st.button(
        "Start over",
        type="primary",
        use_container_width=True,
        on_click=restart_activity,
    )


initialize_state()
render_header()
apply_pending_scroll_reset()
render_stage_row()
render_sidebar()

stage_renderers = (
    render_welcome,
    render_transaction_inbox,
    render_equation_lab,
    render_statement_builder,
    render_debrief,
)
stage_renderers[st.session_state.bbc_stage]()
sync_progress_query(st.session_state, st.query_params)
