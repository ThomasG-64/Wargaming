"""Tests for the actual litellm integration boundary — separate from
test_engine.py, which fakes out call_agent entirely and so never
exercises this file. These confirm our request actually reaches
litellm's real completion() function shaped correctly, without needing
a live API key or making a network call, by injecting litellm's own
mock_response feature underneath our real call_agent."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import litellm

from wargame.llm import call_agent


def test_call_agent_routes_through_openrouter_and_parses_response(monkeypatch):
    real_completion = litellm.completion
    captured = {}

    def completion_with_mock(*args, **kwargs):
        captured.update(kwargs)
        kwargs["mock_response"] = "mocked reply text"
        return real_completion(*args, **kwargs)

    monkeypatch.setattr(litellm, "completion", completion_with_mock)

    result = call_agent(
        model="anthropic/claude-3.5-sonnet",
        system_prompt="you are a test agent",
        user_prompt="what do you do?",
        api_key="fake-test-key",
    )

    assert result == "mocked reply text"
    assert captured["model"] == "openrouter/anthropic/claude-3.5-sonnet"
    assert captured["api_key"] == "fake-test-key"
    assert captured["messages"] == [
        {"role": "system", "content": "you are a test agent"},
        {"role": "user", "content": "what do you do?"},
    ]
