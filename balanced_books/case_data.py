"""The fictional first-month case used by The Balanced Books Challenge."""

from dataclasses import dataclass


ACCOUNTING_TRANSACTION = "Accounting transaction"
NOT_ACCOUNTING_TRANSACTION = "Not an accounting transaction"

EVENT_TYPE_OPTIONS = (ACCOUNTING_TRANSACTION, NOT_ACCOUNTING_TRANSACTION)


@dataclass(frozen=True)
class AccountEffect:
    account: str
    amount: int


@dataclass(frozen=True)
class Transaction:
    id: str
    title: str
    event: str
    document: str
    event_type: str
    effects: tuple[AccountEffect, ...]
    choices: tuple[str, ...]
    correct_choice: str
    classification_explanation: str
    equation_explanation: str

    @property
    def is_recordable(self) -> bool:
        return self.event_type == ACCOUNTING_TRANSACTION


TRANSACTIONS = (
    Transaction(
        id="investment",
        title="The business opens",
        event="The owner invests $20,000 cash in Flyer Fuel Coffee Company in exchange for common stock.",
        document="Bank deposit confirmation",
        event_type=ACCOUNTING_TRANSACTION,
        effects=(
            AccountEffect("Cash", 20_000),
            AccountEffect("Common Stock", 20_000),
        ),
        choices=(
            "Cash increases $20,000; Service Revenue increases $20,000",
            "Cash increases $20,000; Common Stock increases $20,000",
            "Cash increases $20,000; Accounts Payable increases $20,000",
            "No accounts change until the business earns revenue",
        ),
        correct_choice="Cash increases $20,000; Common Stock increases $20,000",
        classification_explanation="Total assets and stockholders' equity both increase by the same amount, so the accounting equation changes and remains balanced.",
        equation_explanation="The investment gives the business cash and represents an owner contribution, not revenue.",
    ),
    Transaction(
        id="equipment_cash",
        title="Equipment arrives",
        event="The company purchases coffee equipment for $6,000 cash.",
        document="Equipment invoice marked paid",
        event_type=ACCOUNTING_TRANSACTION,
        effects=(
            AccountEffect("Cash", -6_000),
            AccountEffect("Equipment", 6_000),
        ),
        choices=(
            "Equipment increases $6,000; Accounts Payable increases $6,000",
            "Equipment Expense increases $6,000; Cash decreases $6,000",
            "Cash increases $6,000; Equipment decreases $6,000",
            "Equipment increases $6,000; Cash decreases $6,000",
        ),
        correct_choice="Equipment increases $6,000; Cash decreases $6,000",
        classification_explanation="The composition of assets changes, but total assets do not change. The accounting equation remains balanced.",
        equation_explanation="One asset increases while another asset decreases. Buying equipment is not immediately an expense in this introductory transaction.",
    ),
    Transaction(
        id="supplies_account",
        title="Supplies are purchased on account",
        event="The company purchases cups, lids, and napkins for $1,200 on account.",
        document="Supplier invoice due next month",
        event_type=ACCOUNTING_TRANSACTION,
        effects=(
            AccountEffect("Supplies", 1_200),
            AccountEffect("Accounts Payable", 1_200),
        ),
        choices=(
            "Supplies Expense increases $1,200; Cash decreases $1,200",
            "Supplies increases $1,200; Accounts Payable increases $1,200",
            "Supplies increases $1,200; Cash decreases $1,200",
            "Accounts Receivable increases $1,200; Service Revenue increases $1,200",
        ),
        correct_choice="Supplies increases $1,200; Accounts Payable increases $1,200",
        classification_explanation="Total assets and total liabilities both increase by the same amount, so the accounting equation changes and remains balanced.",
        equation_explanation="The unused supplies are an asset. 'On account' means the company owes the supplier, so Accounts Payable increases and cash is unchanged.",
    ),
    Transaction(
        id="service_cash",
        title="A busy opening day",
        event="The company provides services to customers and receives $2,500 cash.",
        document="Daily sales report and cash receipt",
        event_type=ACCOUNTING_TRANSACTION,
        effects=(
            AccountEffect("Cash", 2_500),
            AccountEffect("Service Revenue", 2_500),
        ),
        choices=(
            "Cash increases $2,500; Service Revenue increases $2,500",
            "Accounts Receivable increases $2,500; Service Revenue increases $2,500",
            "Cash increases $2,500; Common Stock increases $2,500",
            "Cash increases $2,500; Accounts Payable increases $2,500",
        ),
        correct_choice="Cash increases $2,500; Service Revenue increases $2,500",
        classification_explanation="Total assets and stockholders' equity both increase by the same amount, so the accounting equation changes and remains balanced.",
        equation_explanation="The company earned revenue and received cash at the same time.",
    ),
    Transaction(
        id="service_account",
        title="A campus event is billed",
        event="The company provides $1,800 of catering services to a campus organization on account.",
        document="Customer invoice",
        event_type=ACCOUNTING_TRANSACTION,
        effects=(
            AccountEffect("Accounts Receivable", 1_800),
            AccountEffect("Service Revenue", 1_800),
        ),
        choices=(
            "Cash increases $1,800; Service Revenue increases $1,800",
            "Accounts Payable increases $1,800; Service Revenue increases $1,800",
            "Accounts Receivable increases $1,800; Service Revenue increases $1,800",
            "Accounts Receivable increases $1,800; Cash decreases $1,800",
        ),
        correct_choice="Accounts Receivable increases $1,800; Service Revenue increases $1,800",
        classification_explanation="Total assets and stockholders' equity both increase by the same amount, so the accounting equation changes and remains balanced.",
        equation_explanation="The service has been performed, so revenue is earned. Because the customer will pay later, Accounts Receivable increases instead of Cash.",
    ),
    Transaction(
        id="collect_receivable",
        title="The customer pays part of its bill",
        event="The company receives $1,000 cash from the campus organization for part of the amount previously billed.",
        document="Customer payment notice",
        event_type=ACCOUNTING_TRANSACTION,
        effects=(
            AccountEffect("Cash", 1_000),
            AccountEffect("Accounts Receivable", -1_000),
        ),
        choices=(
            "Cash increases $1,000; Service Revenue increases $1,000",
            "Cash increases $1,000; Accounts Receivable decreases $1,000",
            "Cash increases $1,000; Accounts Payable increases $1,000",
            "Accounts Receivable increases $1,000; Service Revenue increases $1,000",
        ),
        correct_choice="Cash increases $1,000; Accounts Receivable decreases $1,000",
        classification_explanation="The composition of assets changes, but total assets do not change. The accounting equation remains balanced.",
        equation_explanation="Revenue was recorded when the service was provided. Collecting the receivable changes the form of the asset but does not create revenue again.",
    ),
    Transaction(
        id="pay_payable",
        title="Part of the supplier bill is paid",
        event="The company pays $700 cash toward the amount owed to the supplies vendor.",
        document="Electronic payment confirmation",
        event_type=ACCOUNTING_TRANSACTION,
        effects=(
            AccountEffect("Cash", -700),
            AccountEffect("Accounts Payable", -700),
        ),
        choices=(
            "Cash decreases $700; Supplies Expense increases $700",
            "Cash decreases $700; Accounts Receivable decreases $700",
            "Cash decreases $700; Accounts Payable decreases $700",
            "Accounts Payable increases $700; Supplies increases $700",
        ),
        correct_choice="Cash decreases $700; Accounts Payable decreases $700",
        classification_explanation="Total assets and total liabilities both decrease by the same amount, so the accounting equation changes and remains balanced.",
        equation_explanation="Paying a previously recorded payable reduces both Cash and Accounts Payable. It does not record the supplies a second time.",
    ),
    Transaction(
        id="rent",
        title="Monthly rent is paid",
        event="The company pays $900 cash for the current month's rental space.",
        document="Rent receipt",
        event_type=ACCOUNTING_TRANSACTION,
        effects=(
            AccountEffect("Cash", -900),
            AccountEffect("Rent Expense", 900),
        ),
        choices=(
            "Cash decreases $900; Rent Expense increases $900",
            "Cash decreases $900; Equipment increases $900",
            "Accounts Payable decreases $900; Rent Expense increases $900",
            "Cash decreases $900; Dividends increases $900",
        ),
        correct_choice="Cash decreases $900; Rent Expense increases $900",
        classification_explanation="Total assets and stockholders' equity both decrease by the same amount, so the accounting equation changes and remains balanced.",
        equation_explanation="The rental space was used during the current month, so the cost is a current-period expense.",
    ),
    Transaction(
        id="supplies_used",
        title="The supplies count is completed",
        event="A supplies count shows that $500 of cups, lids, and napkins were used during the month.",
        document="End-of-month supplies count",
        event_type=ACCOUNTING_TRANSACTION,
        effects=(
            AccountEffect("Supplies", -500),
            AccountEffect("Supplies Expense", 500),
        ),
        choices=(
            "Supplies decreases $500; Supplies Expense increases $500",
            "Cash decreases $500; Supplies Expense increases $500",
            "Supplies increases $500; Accounts Payable increases $500",
            "Supplies decreases $500; Accounts Payable decreases $500",
        ),
        correct_choice="Supplies decreases $500; Supplies Expense increases $500",
        classification_explanation="Total assets and stockholders' equity both decrease by the same amount, so the accounting equation changes and remains balanced.",
        equation_explanation="Supplies begin as an asset while available for future use. The portion used becomes an expense and reduces the remaining Supplies asset.",
    ),
    Transaction(
        id="dividend",
        title="Cash is distributed to the owner",
        event="The company pays a $600 cash distribution to its owner.",
        document="Owner distribution authorization",
        event_type=ACCOUNTING_TRANSACTION,
        effects=(
            AccountEffect("Cash", -600),
            AccountEffect("Dividends", 600),
        ),
        choices=(
            "Cash decreases $600; Dividends increases $600",
            "Cash decreases $600; Dividend Expense increases $600",
            "Cash decreases $600; Accounts Payable decreases $600",
            "Cash decreases $600; Rent Expense increases $600",
        ),
        correct_choice="Cash decreases $600; Dividends increases $600",
        classification_explanation="Total assets and stockholders' equity both decrease by the same amount. Because the accounting equation changes, this is an accounting transaction.",
        equation_explanation="This is an accounting transaction because Cash and Dividends change. The distribution is not an expense and does not affect revenue or net income; it reduces retained earnings through the retained earnings statement.",
    ),
    Transaction(
        id="future_contract",
        title="A future event is scheduled",
        event="The owner signs a contract to provide coffee service at an event next month. No service has been provided and no payment has been received.",
        document="Signed service agreement",
        event_type=NOT_ACCOUNTING_TRANSACTION,
        effects=(),
        choices=(),
        correct_choice="",
        classification_explanation="No asset, liability, or stockholders' equity total changes yet, so nothing enters the accounting records.",
        equation_explanation="",
    ),
)


RECORDABLE_TRANSACTIONS = tuple(
    transaction for transaction in TRANSACTIONS if transaction.is_recordable
)


STATEMENT_FIELDS = (
    ("Income Statement", "service_revenue", "Service revenue", 4_300),
    ("Income Statement", "rent_expense", "Rent expense", 900),
    ("Income Statement", "supplies_expense", "Supplies expense", 500),
    ("Income Statement", "net_income", "Net income", 2_900),
    ("Retained Earnings Statement", "beginning_retained_earnings", "Beginning retained earnings", 0),
    ("Retained Earnings Statement", "re_net_income", "Add: Net income", 2_900),
    ("Retained Earnings Statement", "dividends", "Less: Dividends", 600),
    ("Retained Earnings Statement", "ending_retained_earnings", "Ending retained earnings", 2_300),
    ("Classified Balance Sheet", "cash", "Cash", 15_300),
    ("Classified Balance Sheet", "accounts_receivable", "Accounts receivable", 800),
    ("Classified Balance Sheet", "supplies", "Supplies", 700),
    ("Classified Balance Sheet", "equipment", "Equipment", 6_000),
    ("Classified Balance Sheet", "total_assets", "Total assets", 22_800),
    ("Classified Balance Sheet", "accounts_payable", "Accounts payable", 500),
    ("Classified Balance Sheet", "common_stock", "Common stock", 20_000),
    ("Classified Balance Sheet", "bs_retained_earnings", "Retained earnings", 2_300),
    ("Classified Balance Sheet", "total_liabilities_equity", "Total liabilities and stockholders' equity", 22_800),
)
