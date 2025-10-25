"""Tests for CSV export helpers used by the Flask API."""

from __future__ import annotations

from typing import Dict, Any

import pytest

try:  # Flask is optional during unit testing
    from src.backend.routes import exports
except ModuleNotFoundError as exc:  # pragma: no cover - environment dependent
    exports = None  # type: ignore[assignment]
    MISSING_FLASK = True
else:
    MISSING_FLASK = False

pytestmark = pytest.mark.skipif(MISSING_FLASK, reason="Flask is not installed")


def _sample_output() -> Dict[str, Any]:
    return {
        "epics": [
            {
                "epic_id": "E-42",
                "Epic": "Checkout",
                "UserStories": [
                    {"title": "Review cart"},
                    {"title": "Pay securely"},
                ],
                "TestCases": [
                    {
                        "id": "TC-01",
                        "objective": "Cart shows all items",
                        "expected_result": "Line items and totals appear",
                    },
                    {
                        "id": "TC-02",
                        "objective": "Payment succeeds",
                        "expected_result": "Confirmation page is displayed",
                    },
                ],
            }
        ]
    }


def test_get_flat_rows_aligns_stories_with_cases() -> None:
    output = _sample_output()

    rows = exports._get_flat_rows(output)

    assert rows == [
        ["E-42", "Review cart", "TC-01: Cart shows all items → Line items and totals appear"],
        ["E-42", "Pay securely", "TC-02: Payment succeeds → Confirmation page is displayed"],
    ]


def test_to_csv_includes_header_and_bom() -> None:
    output = _sample_output()

    csv_text = exports.to_csv(output)

    assert csv_text.startswith("\ufeff")
    lines = csv_text.lstrip("\ufeff").splitlines()
    assert lines[0] == "Epic ID,Story,Test Case"
    assert len(lines) == 3  # header + two rows