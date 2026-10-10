"""Compact, validated URL snapshots for refresh-safe activity progress."""

from __future__ import annotations

import base64
import json
import zlib
from collections.abc import MutableMapping
from typing import Any

from balanced_books.case_data import EVENT_TYPE_OPTIONS, RECORDABLE_TRANSACTIONS, TRANSACTIONS
from balanced_books.engine import evaluate_equation_choice, evaluate_event_type


SNAPSHOT_PARAM = "progress"
SNAPSHOT_VERSION = 1
MAX_TOKEN_LENGTH = 12_000
MAX_JSON_BYTES = 24_000

ACCOUNT_IDS = (
    "cash",
    "accounts_receivable",
    "supplies",
    "equipment",
    "accounts_payable",
    "common_stock",
    "service_revenue",
    "rent_expense",
    "supplies_expense",
    "dividends",
)
STATEMENT_TILES = (
    set(ACCOUNT_IDS),
    set(ACCOUNT_IDS) | {"net_income"},
    set(ACCOUNT_IDS) | {"ending_retained_earnings"},
)
STATEMENT_ZONES = (
    {"operating_revenue", "operating_expenses", "other_items"},
    {"additions", "subtractions"},
    {
        "current_assets",
        "long_term_investments",
        "ppe",
        "intangible_assets",
        "current_liabilities",
        "long_term_liabilities",
        "equity",
    },
)
STATEMENT_EXPECTED = (
    {
        "service_revenue": "operating_revenue",
        "rent_expense": "operating_expenses",
        "supplies_expense": "operating_expenses",
    },
    {"net_income": "additions", "dividends": "subtractions"},
    {
        "cash": "current_assets",
        "accounts_receivable": "current_assets",
        "supplies": "current_assets",
        "equipment": "ppe",
        "accounts_payable": "current_liabilities",
        "common_stock": "equity",
        "ending_retained_earnings": "equity",
    },
)
FEEDBACK_KIND_TO_CODE = {None: 0, "review": 1, "success": 2}
FEEDBACK_CODE_TO_KIND = {value: key for key, value in FEEDBACK_KIND_TO_CODE.items()}


def activity_defaults() -> dict[str, Any]:
    """Return fresh session defaults for one activity attempt."""

    return {
        "bbc_stage": 0,
        "bbc_inbox_index": 0,
        "bbc_inbox_responses": {},
        "bbc_inbox_feedback": {},
        "bbc_inbox_warning": None,
        "bbc_equation_index": 0,
        "bbc_equation_responses": {},
        "bbc_equation_feedback": {},
        "bbc_equation_warning": None,
        "bbc_statement_progress": None,
        "bbc_statement_completion": None,
        "bbc_scroll_token": 1,
        "bbc_scroll_applied": 0,
    }


def encode_snapshot(snapshot: dict[str, Any]) -> str:
    """Encode a snapshot as compact URL-safe compressed JSON."""

    payload = json.dumps(snapshot, separators=(",", ":"), sort_keys=True).encode("utf-8")
    compressed = zlib.compress(payload, level=9)
    return base64.urlsafe_b64encode(compressed).decode("ascii").rstrip("=")


def decode_snapshot(token: object) -> dict[str, Any] | None:
    """Decode and validate an untrusted snapshot token."""

    if not isinstance(token, str) or not token or len(token) > MAX_TOKEN_LENGTH:
        return None
    try:
        padding = "=" * (-len(token) % 4)
        compressed = base64.b64decode(token + padding, altchars=b"-_", validate=True)
        decompressor = zlib.decompressobj()
        payload = decompressor.decompress(compressed, MAX_JSON_BYTES + 1)
        if len(payload) > MAX_JSON_BYTES or decompressor.unconsumed_tail:
            return None
        payload += decompressor.flush(MAX_JSON_BYTES + 1 - len(payload))
        if len(payload) > MAX_JSON_BYTES or decompressor.unused_data:
            return None
        raw = json.loads(payload.decode("utf-8"))
        return validate_snapshot(raw)
    except (ValueError, TypeError, UnicodeDecodeError, json.JSONDecodeError, zlib.error):
        return None


def _require_int(value: object, minimum: int, maximum: int) -> int:
    if type(value) is not int or not minimum <= value <= maximum:
        raise ValueError("Invalid integer value")
    return value


def _validate_answer_map(
    raw: object,
    items,
    option_getter,
    expected_getter,
) -> dict[str, list[object]]:
    if not isinstance(raw, dict):
        raise ValueError("Answer map must be an object")
    ids = [item.id for item in items]
    if set(raw) != set(ids[: len(raw)]):
        raise ValueError("Submitted answers must form a prefix")
    normalized: dict[str, list[object]] = {}
    for item in items[: len(raw)]:
        pair = raw[item.id]
        if not isinstance(pair, list) or len(pair) != 2:
            raise ValueError("Answer entry must contain the selection and result")
        selected, result = pair
        if not isinstance(selected, str) or selected not in option_getter(item):
            raise ValueError("Unknown answer selection")
        correct = selected == expected_getter(item)
        if type(result) is not int or result not in (0, 1) or bool(result) != correct:
            raise ValueError("Answer result does not match the selection")
        normalized[item.id] = [selected, int(correct)]
    return normalized


def validate_component_progress(raw: object) -> dict[str, Any] | None:
    """Validate the descriptive progress payload returned by the custom component."""

    if raw is None:
        return None
    expected_keys = {
        "stage",
        "finalized",
        "placements",
        "selected",
        "attempts",
        "feedbackKinds",
        "shuffledAccountIds",
    }
    if not isinstance(raw, dict) or set(raw) != expected_keys:
        return None
    try:
        stage = _require_int(raw["stage"], 0, 2)
        finalized_raw = raw["finalized"]
        placements_raw = raw["placements"]
        attempts_raw = raw["attempts"]
        feedback_raw = raw["feedbackKinds"]
        order_raw = raw["shuffledAccountIds"]
        if not all(isinstance(value, list) and len(value) == 3 for value in (finalized_raw, placements_raw, attempts_raw, feedback_raw)):
            raise ValueError("Statement arrays must have three entries")

        finalized = []
        for value in finalized_raw:
            if type(value) is not bool:
                raise ValueError("Finalized flags must be booleans")
            finalized.append(value)
        if any(finalized[index] and not finalized[index - 1] for index in range(1, 3)):
            raise ValueError("Statements must be finalized in order")

        placements: list[dict[str, str]] = []
        for index, value in enumerate(placements_raw):
            if not isinstance(value, dict):
                raise ValueError("Placements must be objects")
            normalized_placements: dict[str, str] = {}
            for tile_id, zone_id in value.items():
                if tile_id not in STATEMENT_TILES[index] or zone_id not in STATEMENT_ZONES[index]:
                    raise ValueError("Unknown statement placement")
                normalized_placements[tile_id] = zone_id
            if finalized[index] and normalized_placements != STATEMENT_EXPECTED[index]:
                raise ValueError("Finalized statement placements are incomplete")
            placements.append(normalized_placements)

        attempts = [_require_int(value, 0, 999) for value in attempts_raw]
        feedback_kinds: list[str | None] = []
        for index, value in enumerate(feedback_raw):
            if value not in FEEDBACK_KIND_TO_CODE:
                raise ValueError("Unknown feedback kind")
            if finalized[index] != (value == "success"):
                raise ValueError("Feedback and finalization disagree")
            if value == "review" and attempts[index] == 0:
                raise ValueError("Review feedback requires an attempt")
            if attempts[index] == 0 and value is not None:
                raise ValueError("Feedback requires an attempt")
            feedback_kinds.append(value)

        if not isinstance(order_raw, list) or len(order_raw) != len(ACCOUNT_IDS):
            raise ValueError("Account order is incomplete")
        if any(not isinstance(value, str) for value in order_raw) or set(order_raw) != set(ACCOUNT_IDS):
            raise ValueError("Account order is invalid")

        first_unfinished = next((index for index, value in enumerate(finalized) if not value), None)
        if first_unfinished is not None and not (finalized[stage] or stage == first_unfinished):
            raise ValueError("Current statement is not available")

        selected = raw["selected"]
        if selected is not None:
            if not isinstance(selected, str) or selected not in STATEMENT_TILES[stage]:
                raise ValueError("Selected statement tile is invalid")
            if finalized[stage] or selected in placements[stage]:
                raise ValueError("Selected statement tile is unavailable")

        return {
            "stage": stage,
            "finalized": finalized,
            "placements": placements,
            "selected": selected,
            "attempts": attempts,
            "feedbackKinds": feedback_kinds,
            "shuffledAccountIds": list(order_raw),
        }
    except (TypeError, ValueError):
        return None


def _compact_component_progress(progress: dict[str, Any] | None) -> dict[str, Any] | None:
    normalized = validate_component_progress(progress)
    if normalized is None:
        return None
    return {
        "g": normalized["stage"],
        "f": [int(value) for value in normalized["finalized"]],
        "p": normalized["placements"],
        "s": normalized["selected"],
        "a": normalized["attempts"],
        "r": [FEEDBACK_KIND_TO_CODE[value] for value in normalized["feedbackKinds"]],
        "o": normalized["shuffledAccountIds"],
    }


def _expand_component_progress(raw: object) -> dict[str, Any] | None:
    if raw is None:
        return None
    if not isinstance(raw, dict) or set(raw) != {"g", "f", "p", "s", "a", "r", "o"}:
        raise ValueError("Invalid statement progress")
    finalized = raw["f"]
    feedback = raw["r"]
    if not isinstance(finalized, list) or any(type(value) is not int or value not in (0, 1) for value in finalized):
        raise ValueError("Invalid finalized flags")
    if not isinstance(feedback, list) or any(type(value) is not int or value not in FEEDBACK_CODE_TO_KIND for value in feedback):
        raise ValueError("Invalid feedback codes")
    expanded = {
        "stage": raw["g"],
        "finalized": [bool(value) for value in finalized],
        "placements": raw["p"],
        "selected": raw["s"],
        "attempts": raw["a"],
        "feedbackKinds": [FEEDBACK_CODE_TO_KIND[value] for value in feedback],
        "shuffledAccountIds": raw["o"],
    }
    normalized = validate_component_progress(expanded)
    if normalized is None:
        raise ValueError("Invalid statement progress")
    return normalized


def validate_snapshot(raw: object) -> dict[str, Any] | None:
    """Validate an untrusted decoded snapshot and return its normalized form."""

    expected_keys = {"v", "s", "ii", "ir", "ic", "ei", "er", "ec", "sp", "c"}
    if not isinstance(raw, dict) or set(raw) != expected_keys or raw.get("v") != SNAPSHOT_VERSION:
        return None
    try:
        stage = _require_int(raw["s"], 0, 4)
        inbox_index = _require_int(raw["ii"], 0, len(TRANSACTIONS) - 1)
        equation_index = _require_int(raw["ei"], 0, len(RECORDABLE_TRANSACTIONS) - 1)
        inbox_results = _validate_answer_map(
            raw["ir"],
            TRANSACTIONS,
            lambda _item: EVENT_TYPE_OPTIONS,
            lambda item: item.event_type,
        )
        equation_results = _validate_answer_map(
            raw["er"],
            RECORDABLE_TRANSACTIONS,
            lambda item: item.choices,
            lambda item: item.correct_choice,
        )
        inbox_choice = raw["ic"]
        equation_choice = raw["ec"]
        statement_progress = _expand_component_progress(raw["sp"])
        completion = raw["c"]

        if stage == 0:
            if inbox_index != 0 or inbox_results or inbox_choice is not None or equation_index != 0 or equation_results or equation_choice is not None or statement_progress is not None or completion is not None:
                raise ValueError("Welcome snapshot contains activity progress")
        elif stage == 1:
            if len(inbox_results) not in {inbox_index, inbox_index + 1}:
                raise ValueError("Inbox index does not match submitted answers")
            if len(inbox_results) == inbox_index:
                if inbox_choice is not None and inbox_choice not in EVENT_TYPE_OPTIONS:
                    raise ValueError("Invalid inbox choice")
            elif inbox_choice is not None:
                raise ValueError("Submitted inbox item cannot also have a draft choice")
            if equation_index != 0 or equation_results or equation_choice is not None or statement_progress is not None or completion is not None:
                raise ValueError("Inbox snapshot contains later-stage progress")
        elif stage == 2:
            if inbox_index != len(TRANSACTIONS) - 1 or len(inbox_results) != len(TRANSACTIONS) or inbox_choice is not None:
                raise ValueError("Inbox must be complete")
            if len(equation_results) not in {equation_index, equation_index + 1}:
                raise ValueError("Equation index does not match submitted answers")
            if len(equation_results) == equation_index:
                current = RECORDABLE_TRANSACTIONS[equation_index]
                if equation_choice is not None and equation_choice not in current.choices:
                    raise ValueError("Invalid equation choice")
            elif equation_choice is not None:
                raise ValueError("Submitted equation item cannot also have a draft choice")
            if statement_progress is not None or completion is not None:
                raise ValueError("Equation snapshot contains later-stage progress")
        else:
            if inbox_index != len(TRANSACTIONS) - 1 or len(inbox_results) != len(TRANSACTIONS) or inbox_choice is not None:
                raise ValueError("Inbox must be complete")
            if equation_index != len(RECORDABLE_TRANSACTIONS) - 1 or len(equation_results) != len(RECORDABLE_TRANSACTIONS) or equation_choice is not None:
                raise ValueError("Equation Lab must be complete")
            if stage == 3 and completion is not None:
                raise ValueError("Statement Builder snapshot cannot be complete")
            if stage == 4:
                if statement_progress is None or statement_progress["finalized"] != [True, True, True]:
                    raise ValueError("Debrief requires three finalized statements")
                if not isinstance(completion, list) or len(completion) != 2:
                    raise ValueError("Debrief completion is missing")
                finalized_count = _require_int(completion[0], 0, 3)
                attempts = _require_int(completion[1], 0, 2_997)
                if finalized_count != 3 or attempts != sum(statement_progress["attempts"]):
                    raise ValueError("Completion summary does not match statement progress")

        return {
            "v": SNAPSHOT_VERSION,
            "s": stage,
            "ii": inbox_index,
            "ir": inbox_results,
            "ic": inbox_choice,
            "ei": equation_index,
            "er": equation_results,
            "ec": equation_choice,
            "sp": _compact_component_progress(statement_progress),
            "c": completion,
        }
    except (TypeError, ValueError):
        return None


def snapshot_from_session(session_state: MutableMapping[str, Any]) -> dict[str, Any]:
    """Build and validate a compact snapshot from trusted session state."""

    inbox_responses = session_state.get("bbc_inbox_responses", {})
    equation_responses = session_state.get("bbc_equation_responses", {})
    if not isinstance(inbox_responses, dict) or not isinstance(equation_responses, dict):
        raise ValueError("Response state is invalid")
    known_inbox = {item.id: item for item in TRANSACTIONS}
    known_equation = {item.id: item for item in RECORDABLE_TRANSACTIONS}
    if not set(inbox_responses).issubset(known_inbox) or not set(equation_responses).issubset(known_equation):
        raise ValueError("Response state contains unknown items")

    inbox_results = {
        item.id: [inbox_responses[item.id], int(inbox_responses[item.id] == item.event_type)]
        for item in TRANSACTIONS
        if item.id in inbox_responses
    }
    equation_results = {
        item.id: [equation_responses[item.id], int(equation_responses[item.id] == item.correct_choice)]
        for item in RECORDABLE_TRANSACTIONS
        if item.id in equation_responses
    }
    stage = session_state.get("bbc_stage", 0)
    inbox_index = session_state.get("bbc_inbox_index", 0)
    equation_index = session_state.get("bbc_equation_index", 0)

    inbox_choice = None
    if stage == 1 and 0 <= inbox_index < len(TRANSACTIONS):
        current = TRANSACTIONS[inbox_index]
        if current.id not in inbox_responses:
            inbox_choice = session_state.get(f"inbox_choice_{current.id}")

    equation_choice = None
    if stage == 2 and 0 <= equation_index < len(RECORDABLE_TRANSACTIONS):
        current = RECORDABLE_TRANSACTIONS[equation_index]
        if current.id not in equation_responses:
            equation_choice = session_state.get(f"equation_choice_{current.id}")

    completion_state = session_state.get("bbc_statement_completion")
    completion = None
    if completion_state is not None:
        if not isinstance(completion_state, dict):
            raise ValueError("Completion state is invalid")
        completion = [
            completion_state.get("statementsFinalized"),
            completion_state.get("attempts"),
        ]

    raw = {
        "v": SNAPSHOT_VERSION,
        "s": stage,
        "ii": inbox_index,
        "ir": inbox_results,
        "ic": inbox_choice,
        "ei": equation_index,
        "er": equation_results,
        "ec": equation_choice,
        "sp": _compact_component_progress(session_state.get("bbc_statement_progress")),
        "c": completion,
    }
    normalized = validate_snapshot(raw)
    if normalized is None:
        raise ValueError("Session state cannot be represented as a valid progress snapshot")
    return normalized


def restore_session_state(session_state: MutableMapping[str, Any], token: object) -> bool:
    """Restore validated progress into a new session and regenerate feedback."""

    snapshot = decode_snapshot(token)
    if snapshot is None:
        return False
    clear_activity_state(session_state)
    session_state.update(activity_defaults())
    session_state["bbc_stage"] = snapshot["s"]
    session_state["bbc_inbox_index"] = snapshot["ii"]
    session_state["bbc_equation_index"] = snapshot["ei"]

    inbox_responses = {item_id: pair[0] for item_id, pair in snapshot["ir"].items()}
    equation_responses = {item_id: pair[0] for item_id, pair in snapshot["er"].items()}
    inbox_by_id = {item.id: item for item in TRANSACTIONS}
    equation_by_id = {item.id: item for item in RECORDABLE_TRANSACTIONS}
    session_state["bbc_inbox_responses"] = inbox_responses
    session_state["bbc_inbox_feedback"] = {
        item_id: evaluate_event_type(inbox_by_id[item_id], selected)
        for item_id, selected in inbox_responses.items()
    }
    session_state["bbc_equation_responses"] = equation_responses
    session_state["bbc_equation_feedback"] = {
        item_id: evaluate_equation_choice(equation_by_id[item_id], selected)
        for item_id, selected in equation_responses.items()
    }

    if snapshot["ic"] is not None:
        current = TRANSACTIONS[snapshot["ii"]]
        session_state[f"inbox_choice_{current.id}"] = snapshot["ic"]
    if snapshot["ec"] is not None:
        current = RECORDABLE_TRANSACTIONS[snapshot["ei"]]
        session_state[f"equation_choice_{current.id}"] = snapshot["ec"]

    statement_progress = _expand_component_progress(snapshot["sp"])
    session_state["bbc_statement_progress"] = statement_progress
    if snapshot["c"] is not None:
        session_state["bbc_statement_completion"] = {
            "completed": True,
            "statementsFinalized": snapshot["c"][0],
            "attempts": snapshot["c"][1],
        }
    return True


def clear_activity_state(session_state: MutableMapping[str, Any]) -> None:
    """Remove activity and widget state without touching unrelated session data."""

    prefixes = (
        "bbc_",
        "stmt_",
        "inbox_choice_",
        "equation_choice_",
        "statement_builder_workspace_",
    )
    for key in list(session_state):
        if key.startswith(prefixes):
            del session_state[key]


def sync_progress_query(
    session_state: MutableMapping[str, Any],
    query_params: MutableMapping[str, Any],
) -> str:
    """Replace the saved URL snapshot when the trusted session state changes."""

    token = encode_snapshot(snapshot_from_session(session_state))
    if query_params.get(SNAPSHOT_PARAM) != token:
        query_params[SNAPSHOT_PARAM] = token
    return token


def reset_saved_progress(
    session_state: MutableMapping[str, Any],
    query_params: MutableMapping[str, Any],
) -> str:
    """Start a fresh attempt and immediately replace the saved URL state."""

    clear_activity_state(session_state)
    session_state.update(activity_defaults())
    session_state["bbc_restore_attempted"] = True
    return sync_progress_query(session_state, query_params)
