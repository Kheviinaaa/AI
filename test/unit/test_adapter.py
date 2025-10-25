"""Tests for adapting AI engine output into export friendly structures."""

from __future__ import annotations

from src.backend.services.adapter import adapt_ai_engine_epic


def test_adapt_ai_engine_epic_generates_consistent_ids() -> None:
    epic = {
        "Epic": "Checkout",
        "epic_id": "E-123",
        "UserStories": [
            {
                "title": "Review cart",
                "description": "As a shopper I see my items",
                "acceptance_criteria": {
                    "Given": "Items in cart",
                    "When": "Cart viewed",
                    "Then": "All items visible",
                },
                "story_points": 5,
            },
            {
                "title": "Pay securely",
                "description": "As a shopper I pay safely",
                "acceptance_criteria": {
                    "Given": "Valid payment",
                    "When": "Payment submitted",
                    "Then": "Order confirmed",
                },
                "story_points": 8,
            },
        ],
        "TestCases": [
            {
                "id": "TC-01",
                "objective": "Cart displays",
                "preconditions": "Items exist",
                "test_steps": ["Open cart"],
                "expected_result": "Items visible",
            }
        ],
    }

    adapted = adapt_ai_engine_epic(epic)

    assert adapted["epic_id"] == "E-123"
    assert [story["story_id"] for story in adapted["stories"]] == ["US-01", "US-02"]
    assert adapted["stories"][0]["title"] == "Review cart"
    assert adapted["test_cases"][0]["id"] == "TC-01"