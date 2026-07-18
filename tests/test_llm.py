"""Tests for the actual model-call integration boundary — separate from
test_engine.py, which fakes out call_agent entirely and so never
exercises this file. The openrouter tests confirm our request reaches
litellm's real completion() function shaped correctly (via litellm's own
mock_response feature); the claude_code tests confirm our request
reaches the Claude Agent SDK's query() shaped correctly (by stubbing
query, the same seam the alignment-data-pipeline repo stubs). Neither
needs a live key, a network call, or the actual CLI."""

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


# --- claude_code backend ---

def make_result_message(**overrides):
    from claude_agent_sdk.types import ResultMessage

    defaults = dict(
        subtype="success",
        duration_ms=1,
        duration_api_ms=1,
        is_error=False,
        num_turns=1,
        session_id="test-session",
        result="cli reply text",
    )
    defaults.update(overrides)
    return ResultMessage(**defaults)


def stub_query(monkeypatch, messages, captured):
    """Replace claude_agent_sdk.query with an async generator yielding
    `messages`. llm.py imports query lazily at call time, so patching the
    module attribute is enough."""
    import claude_agent_sdk

    async def fake_query(*, prompt, options):
        captured["prompt"] = prompt
        captured["options"] = options
        for msg in messages:
            yield msg

    monkeypatch.setattr(claude_agent_sdk, "query", fake_query)


def test_call_agent_claude_code_backend_runs_one_toolless_cli_turn(monkeypatch):
    from claude_agent_sdk.types import AssistantMessage, TextBlock

    captured = {}
    stub_query(
        monkeypatch,
        [
            AssistantMessage(content=[TextBlock(text="cli reply text")], model="claude-haiku-4-5"),
            make_result_message(),
        ],
        captured,
    )

    result = call_agent(
        model="claude-haiku-4-5",
        system_prompt="you are a test agent",
        user_prompt="what do you do?",
        api_key="",  # ignored on this backend
        backend="claude_code",
    )

    assert result == "cli reply text"
    assert captured["prompt"] == "what do you do?"
    options = captured["options"]
    assert options.model == "claude-haiku-4-5"
    assert options.system_prompt == "you are a test agent"
    # Plain text generation, hermetic, and unable to bill an ambient API key.
    assert options.tools == []
    assert options.max_turns == 1
    assert options.setting_sources == []
    assert options.env == {"ANTHROPIC_API_KEY": "", "ANTHROPIC_AUTH_TOKEN": ""}


def test_call_agent_claude_code_error_result_raises_with_cli_message(monkeypatch):
    import pytest

    stub_query(
        monkeypatch,
        [make_result_message(is_error=True, subtype="error", result="Claude AI usage limit reached")],
        {},
    )

    with pytest.raises(RuntimeError, match="usage limit reached"):
        call_agent(
            model="claude-haiku-4-5",
            system_prompt="s",
            user_prompt="u",
            api_key="",
            backend="claude_code",
        )


def test_call_agent_rejects_unknown_backend():
    import pytest

    with pytest.raises(ValueError, match="Unknown backend"):
        call_agent(model="m", system_prompt="s", user_prompt="u", api_key="k", backend="banana")
