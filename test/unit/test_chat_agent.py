"""Unit tests for the conversational agent exposed in :mod:`src.chat_agent`."""

from __future__ import annotations

import textwrap
from typing import Any, Dict

import pytest

from src import chat_agent


@pytest.fixture()
def agent(monkeypatch: pytest.MonkeyPatch) -> chat_agent.EpicChatAgent:
    """Provide a fresh agent with the AI engine patched out."""

    monkeypatch.setattr(chat_agent.ai_engine, "using_live_model", lambda: False)
    sample_payload: Dict[str, Any] = {
        "Epic": "Mock Epic",
        "description": "Demo description",
        "UserStories": [
            {
                "title": "Review cart",
                "description": "As a shopper...",
                "story_points": 5,
                "acceptance_criteria": {
                    "Given": "items in basket",
                    "When": "user checks out",
                    "Then": "totals visible",
                },
            }
        ],
        "TestCases": [
            {
                "id": "TC-01",
                "objective": "Verify cart",
                "preconditions": "Cart has items",
                "test_steps": ["Navigate to cart"],
                "expected_result": "Cart details shown",
            }
        ],
    }

    def fake_generate(prompt: str, epic_title: str | None) -> Dict[str, Any]:
        fake_generate.called_with = (prompt, epic_title)
        return sample_payload

    fake_generate.called_with = (None, None)  # type: ignore[attr-defined]
    monkeypatch.setattr(chat_agent.ai_engine, "generate_user_stories", fake_generate)

    agent = chat_agent.EpicChatAgent()
    agent._last_payload = None
    return agent


def test_help_command_mentions_available_actions(agent: chat_agent.EpicChatAgent) -> None:
    response = agent.respond("help")

    assert response.role == "assistant"
    assert "I am an Agile planning assistant" in response.content
    assert "Type \"exit\"" in response.content
    assert agent._last_payload is None
    assert [message.role for message in agent.history] == ["user", "assistant"]


def test_generation_prompt_returns_structured_payload(agent: chat_agent.EpicChatAgent) -> None:
    response = agent.respond("Please generate user stories for checkout")

    assert response.role == "assistant"
    assert "Epic: Mock Epic" in response.content
    assert "User Stories:" in response.content
    assert "Test Cases:" in response.content
    assert response.payload is not None
    assert response.payload["Epic"] == "Mock Epic"

    # The patched ai_engine should have been invoked with the original prompt.
    assert agent.history[0].content == "Please generate user stories for checkout"
    assert agent.history[-1] is response
    assert chat_agent.ai_engine.generate_user_stories.called_with == (
        "Please generate user stories for checkout",
        None,
    )


def test_exit_command_does_not_trigger_generation(agent: chat_agent.EpicChatAgent) -> None:
    response = agent.respond("exit")

    assert response.content.startswith("Thanks for chatting")
    # Ensure generation helper was not called.
    assert chat_agent.ai_engine.generate_user_stories.called_with == (None, None)
    assert [message.role for message in agent.history] == ["user", "assistant"]


def test_unknown_prompt_returns_fallback(agent: chat_agent.EpicChatAgent) -> None:
    response = agent.respond("What can you do?")

    expected = textwrap.dedent(
        """
        I can generate Agile user stories and test cases for the epics or features you describe.
        Try asking me something like "Generate user stories for a mobile banking login epic".
        Type "help" to see all commands or "exit" to leave the chat.
        """
    ).strip()

    assert response.content == expected
    assert chat_agent.ai_engine.generate_user_stories.called_with == (None, None)
    assert [message.role for message in agent.history] == ["user", "assistant"]


def test_empty_prompt_requests_input(agent: chat_agent.EpicChatAgent) -> None:
    response = agent.respond("   ")

    assert response.content == "Please type a request so I can help you."
    # No new messages should have been stored besides the assistant reply.
    assert agent.history == []
    assert chat_agent.ai_engine.generate_user_stories.called_with == (None, None)