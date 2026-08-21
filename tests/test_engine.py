import unittest

from balanced_books.case_data import (
    ACCOUNTING_TRANSACTION,
    NOT_ACCOUNTING_TRANSACTION,
    RECORDABLE_TRANSACTIONS,
    STATEMENT_FIELDS,
    TRANSACTIONS,
)
from balanced_books.engine import (
    balances_after,
    equation_components,
    evaluate_equation_choice,
    evaluate_event_type,
    evaluate_statement_responses,
    statement_values_from_balances,
)


class CaseDataTests(unittest.TestCase):
    def test_transaction_ids_are_unique(self):
        ids = [transaction.id for transaction in TRANSACTIONS]
        self.assertEqual(len(ids), len(set(ids)))

    def test_case_uses_only_accounting_or_nonaccounting_classifications(self):
        event_types = {transaction.event_type for transaction in TRANSACTIONS}
        self.assertEqual(event_types, {ACCOUNTING_TRANSACTION, NOT_ACCOUNTING_TRANSACTION})

    def test_recordable_transactions_have_two_effects_and_four_choices(self):
        for transaction in RECORDABLE_TRANSACTIONS:
            with self.subTest(transaction=transaction.id):
                self.assertEqual(len(transaction.effects), 2)
                self.assertEqual(len(transaction.choices), 4)
                self.assertIn(transaction.correct_choice, transaction.choices)

    def test_statement_field_keys_are_unique(self):
        keys = [key for _, key, _, _ in STATEMENT_FIELDS]
        self.assertEqual(len(keys), len(set(keys)))


class TransactionEngineTests(unittest.TestCase):
    def test_accounting_equation_balances_after_every_recordable_transaction(self):
        completed: list[str] = []
        for transaction in RECORDABLE_TRANSACTIONS:
            completed.append(transaction.id)
            equation = equation_components(balances_after(completed))
            with self.subTest(transaction=transaction.id):
                self.assertEqual(equation["assets"], equation["liabilities_and_equity"])

    def test_final_account_balances(self):
        balances = balances_after()
        expected = {
            "Cash": 15_300,
            "Accounts Receivable": 800,
            "Supplies": 700,
            "Equipment": 6_000,
            "Accounts Payable": 500,
            "Common Stock": 20_000,
            "Service Revenue": 4_300,
            "Rent Expense": 900,
            "Supplies Expense": 500,
            "Dividends": 600,
        }
        self.assertEqual(balances, expected)

    def test_final_statement_values(self):
        values = statement_values_from_balances(balances_after())
        self.assertEqual(values["net_income"], 2_900)
        self.assertEqual(values["ending_retained_earnings"], 2_300)
        self.assertEqual(values["total_assets"], 22_800)
        self.assertEqual(values["total_liabilities_equity"], 22_800)

    def test_statement_field_answers_match_calculated_case_values(self):
        values = statement_values_from_balances(balances_after())
        for section, key, _, expected in STATEMENT_FIELDS:
            with self.subTest(section=section, key=key):
                self.assertEqual(expected, values[key])

    def test_event_type_feedback_is_item_specific(self):
        transaction = TRANSACTIONS[0]
        result = evaluate_event_type(transaction, NOT_ACCOUNTING_TRANSACTION)
        self.assertFalse(result["correct"])
        self.assertEqual(result["expected"], ACCOUNTING_TRANSACTION)
        self.assertIn("total assets", result["explanation"].lower())
        self.assertIn("stockholders' equity", result["explanation"].lower())

    def test_classification_feedback_does_not_reveal_specific_accounts(self):
        specific_accounts = {
            "Cash",
            "Accounts Receivable",
            "Supplies",
            "Equipment",
            "Accounts Payable",
            "Common Stock",
            "Service Revenue",
            "Rent Expense",
            "Supplies Expense",
            "Dividends",
        }
        for transaction in TRANSACTIONS:
            with self.subTest(transaction=transaction.id):
                for account in specific_accounts:
                    self.assertNotIn(account.lower(), transaction.classification_explanation.lower())

    def test_owner_distribution_is_an_accounting_transaction_not_an_expense(self):
        distribution = next(transaction for transaction in TRANSACTIONS if transaction.id == "dividend")
        self.assertEqual(distribution.event_type, ACCOUNTING_TRANSACTION)
        self.assertEqual(
            {(effect.account, effect.amount) for effect in distribution.effects},
            {("Cash", -600), ("Dividends", 600)},
        )
        self.assertIn("not an expense", distribution.equation_explanation)

    def test_equipment_purchase_changes_asset_composition_in_running_balances(self):
        balances = balances_after(["investment", "equipment_cash"])
        self.assertEqual(balances["Cash"], 14_000)
        self.assertEqual(balances["Equipment"], 6_000)
        equation = equation_components(balances)
        self.assertEqual(equation["assets"], 20_000)
        self.assertEqual(equation["assets"], equation["liabilities_and_equity"])

    def test_equation_choice_feedback_is_item_specific(self):
        transaction = RECORDABLE_TRANSACTIONS[2]
        result = evaluate_equation_choice(transaction, transaction.choices[0])
        self.assertFalse(result["correct"])
        self.assertEqual(result["expected"], transaction.correct_choice)
        self.assertIn("Accounts Payable", result["explanation"])

    def test_statement_feedback_identifies_each_incorrect_line(self):
        expected = statement_values_from_balances(balances_after())
        responses = expected.copy()
        responses["supplies"] = 1_200
        responses["net_income"] = 3_400
        results = evaluate_statement_responses(responses, expected)
        incorrect = {key for key, result in results.items() if not result["correct"]}
        self.assertEqual(incorrect, {"supplies", "net_income"})


if __name__ == "__main__":
    unittest.main()
