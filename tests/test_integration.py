"""End-to-end test: a real multi-agent, multi-turn game through the real
run_game(), with only litellm's network call mocked out. This is the
strongest confidence we can get that the whole pipeline (config ->
validation -> turn loop -> per-agent calls -> judge adjudication ->
situation chaining) actually works together, without spending a real
API key."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import litellm

from wargame.agents import AgentConfig
from wargame.config import GameConfig
from wargame.engine import run_game
from wargame.judge import JudgeConfig


def test_full_game_runs_end_to_end_with_mocked_model_calls(monkeypatch):
    real_completion = litellm.completion
    call_log = []

    def completion_with_mock(*args, **kwargs):
        call_log.append(kwargs["model"])
        # Each reply is unique (includes a running call count) so we can
        # confirm the situation actually chains turn to turn instead of
        # every turn just repeating the same mocked string.
        kwargs["mock_response"] = f"reply #{len(call_log)} from {kwargs['model']}"
        return real_completion(*args, **kwargs)

    monkeypatch.setattr(litellm, "completion", completion_with_mock)

    config = GameConfig(
        agents=[
            AgentConfig(name="Alpha", objective="win", model="anthropic/claude-3.5-sonnet"),
            AgentConfig(name="Beta", objective="block Alpha", model="openai/gpt-4o"),
        ],
        judge=JudgeConfig(model="anthropic/claude-3.5-sonnet", context="some background"),
        scenario="the opening situation",
        num_turns=3,
        openrouter_api_key="fake-key",
    )

    turns = run_game(config)

    assert len(turns) == 3
    # every agent produced an action every turn
    for turn in turns:
        assert set(turn.actions.keys()) == {"Alpha", "Beta"}
        assert turn.summary  # judge produced a non-empty outcome

    # situation chains forward: turn N's situation is turn N-1's summary
    assert turns[0].situation == "the opening situation"
    assert turns[1].situation == turns[0].summary
    assert turns[2].situation == turns[1].summary

    # 2 agents + 1 judge per turn, 3 turns = 9 real (mocked) litellm calls
    assert len(call_log) == 9
    # both agents' models got prefixed for OpenRouter correctly
    assert "openrouter/anthropic/claude-3.5-sonnet" in call_log
    assert "openrouter/openai/gpt-4o" in call_log
