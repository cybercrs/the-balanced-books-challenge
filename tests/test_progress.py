import unittest

from balanced_books.case_data import RECORDABLE_TRANSACTIONS, TRANSACTIONS
from balanced_books.progress import (
    ACCOUNT_IDS,
    SNAPSHOT_PARAM,
    STATEMENT_EXPECTED,
    activity_defaults,
    decode_snapshot,
    encode_snapshot,
    reset_saved_progress,
    restore_session_state,
    snapshot_from_session,
)


def completed_inbox() -> dict[str, str]:
    return {transaction.id: transaction.event_type for transaction in TRANSACTIONS}


def completed_equation_lab() -> dict[str, str]:
    return {
        transaction.id: transaction.correct_choice
        for transaction in RECORDABLE_TRANSACTIONS
    }


class ProgressSnapshotTests(unittest.TestCase):
    def test_malformed_or_tampered_snapshots_are_rejected(self):
        self.assertIsNone(decode_snapshot("not-a-valid-snapshot"))

        wrong_version = snapshot_from_session(activity_defaults())
        wrong_version["v"] = 99
        self.assertIsNone(decode_snapshot(encode_snapshot(wrong_version)))

        state = activity_defaults()
        state["bbc_stage"] = 2
        state["bbc_inbox_index"] = len(TRANSACTIONS) - 1
        state["bbc_inbox_responses"] = completed_inbox()
        state["bbc_equation_index"] = 1
        first = RECORDABLE_TRANSACTIONS[0]
        state["bbc_equation_responses"] = {first.id: first.correct_choice}
        tampered_result = snapshot_from_session(state)
        tampered_result["er"][first.id][1] = 0
        self.assertIsNone(decode_snapshot(encode_snapshot(tampered_result)))

    def test_mid_activity_restoration_recovers_page_choices_and_results(self):
        state = activity_defaults()
        state["bbc_stage"] = 2
        state["bbc_inbox_index"] = len(TRANSACTIONS) - 1
        state["bbc_inbox_responses"] = completed_inbox()
        state["bbc_equation_index"] = 2
        first, second, current = RECORDABLE_TRANSACTIONS[:3]
        wrong_second_choice = next(
            choice for choice in second.choices if choice != second.correct_choice
        )
        state["bbc_equation_responses"] = {
            first.id: first.correct_choice,
            second.id: wrong_second_choice,
        }
        draft_choice = current.choices[1]
        state[f"equation_choice_{current.id}"] = draft_choice

        token = encode_snapshot(snapshot_from_session(state))
        restored: dict[str, object] = {}
        self.assertTrue(restore_session_state(restored, token))
        self.assertEqual(restored["bbc_stage"], 2)
        self.assertEqual(restored["bbc_equation_index"], 2)
        self.assertEqual(restored[f"equation_choice_{current.id}"], draft_choice)
        self.assertTrue(restored["bbc_equation_feedback"][first.id]["correct"])
        self.assertFalse(restored["bbc_equation_feedback"][second.id]["correct"])

    def test_mid_statement_builder_progress_is_restored(self):
        state = activity_defaults()
        state["bbc_stage"] = 3
        state["bbc_inbox_index"] = len(TRANSACTIONS) - 1
        state["bbc_inbox_responses"] = completed_inbox()
        state["bbc_equation_index"] = len(RECORDABLE_TRANSACTIONS) - 1
        state["bbc_equation_responses"] = completed_equation_lab()
        progress = {
            "stage": 0,
            "finalized": [False, False, False],
            "placements": [
                {
                    "service_revenue": "operating_revenue",
                    "cash": "operating_expenses",
                },
                {},
                {},
            ],
            "selected": "rent_expense",
            "attempts": [1, 0, 0],
            "feedbackKinds": ["review", None, None],
            "shuffledAccountIds": list(reversed(ACCOUNT_IDS)),
        }
        state["bbc_statement_progress"] = progress

        token = encode_snapshot(snapshot_from_session(state))
        restored: dict[str, object] = {}
        self.assertTrue(restore_session_state(restored, token))
        self.assertEqual(restored["bbc_stage"], 3)
        self.assertEqual(restored["bbc_statement_progress"], progress)

    def test_start_over_replaces_saved_state(self):
        state = activity_defaults()
        state["bbc_stage"] = 1
        state["bbc_inbox_index"] = 1
        first = TRANSACTIONS[0]
        state["bbc_inbox_responses"] = {first.id: first.event_type}
        state["inbox_choice_unused"] = "stale widget value"
        query_params = {SNAPSHOT_PARAM: encode_snapshot(snapshot_from_session(state))}
        previous_token = query_params[SNAPSHOT_PARAM]

        replacement = reset_saved_progress(state, query_params)
        self.assertNotEqual(replacement, previous_token)
        self.assertEqual(state["bbc_stage"], 0)
        self.assertEqual(state["bbc_inbox_responses"], {})
        self.assertNotIn("inbox_choice_unused", state)
        self.assertEqual(query_params[SNAPSHOT_PARAM], replacement)
        self.assertEqual(decode_snapshot(replacement)["s"], 0)

    def test_completed_snapshot_restores_completion_status(self):
        state = activity_defaults()
        state["bbc_stage"] = 4
        state["bbc_inbox_index"] = len(TRANSACTIONS) - 1
        state["bbc_inbox_responses"] = completed_inbox()
        state["bbc_equation_index"] = len(RECORDABLE_TRANSACTIONS) - 1
        state["bbc_equation_responses"] = completed_equation_lab()
        state["bbc_statement_progress"] = {
            "stage": 2,
            "finalized": [True, True, True],
            "placements": [dict(expected) for expected in STATEMENT_EXPECTED],
            "selected": None,
            "attempts": [1, 2, 1],
            "feedbackKinds": ["success", "success", "success"],
            "shuffledAccountIds": list(ACCOUNT_IDS),
        }
        state["bbc_statement_completion"] = {
            "completed": True,
            "statementsFinalized": 3,
            "attempts": 4,
        }

        token = encode_snapshot(snapshot_from_session(state))
        restored: dict[str, object] = {}
        self.assertTrue(restore_session_state(restored, token))
        self.assertEqual(restored["bbc_stage"], 4)
        self.assertEqual(restored["bbc_statement_completion"]["attempts"], 4)
        self.assertLess(len(token), 2_000)


if __name__ == "__main__":
    unittest.main()
