"""Tests for the lightweight schema validation helpers."""

from __future__ import annotations

from typing import Dict, Any

from src import validators


def _valid_epic() -> Dict[str, Any]:
    return {
        "Epic": "Checkout",
        "epic_id": "E-1",
        "description": "Complete purchase flow",
        "UserStories": [
            {
                "title": "Review cart",
                "description": "As a shopper I want to review my basket",
                "acceptance_criteria": {
                    "Given": "Items exist",
                    "When": "The user opens the cart",
                    "Then": "Line items are visible",
                },
                "story_points": 5,
            }
        ],
        "TestCases": [
            {
                "id": "TC-01",
                "objective": "Cart shows items",
                "preconditions": "Cart populated",
                "test_steps": ["Navigate to cart"],
                "expected_result": "Items visible",
            }
        ],
    }


def test_validate_output_accepts_valid_payload() -> None:
    payload = [_valid_epic()]

    is_valid, errors = validators.validate_output(payload)

    assert is_valid
    assert errors == []


def test_validate_output_flags_missing_story_fields() -> None:
    epic = _valid_epic()
    epic["UserStories"][0].pop("description")

    is_valid, errors = validators.validate_output([epic])

    assert not is_valid
    assert any("missing field 'description'" in err for err in errors)


def test_validate_output_handles_non_list_input() -> None:
    """Passing a dictionary instead of a list should still be supported."""

    is_valid, errors = validators.validate_output(_valid_epic())

    assert is_valid
    assert errors == []