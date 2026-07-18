"""Smoke tests for the turn-loop plumbing. These don't call any real LLM —
they fake out call_agent so we can run this without an API key."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from wargame import engine
from wargame.agents import AgentConfig
from wargame.config import GameConfig
from wargame.judge import JudgeConfig


def test_run_turn_collects_an_action_per_agent_and_a_summary(monkeypatch):
    # Replace the real LLM call with a fake one that just echoes back
    # which model called it, so we can test the loop's wiring without
    # needing an API key or making network calls.
    def fake_call_agent(model, system_prompt, user_prompt, api_key, backend="openrouter"):
        return f"fake response from {model}"

    monkeypatch.setattr(engine, "call_agent", fake_call_agent)

    agents = [
        AgentConfig(name="A", objective="x", model="model-a"),
        AgentConfig(name="B", objective="y", model="model-b"),
    ]
    judge = JudgeConfig(model="judge-model", context="some context")

    record = engine.run_turn(
        turn_number=1,
        situation="opening situation",
        agents=agents,
        judge=judge,
        api_key="fake-key",
    )

    assert record.turn_number == 1
    assert set(record.actions.keys()) == {"A", "B"}
    assert record.summary == "fake response from judge-model"


def test_run_game_chains_situation_forward(monkeypatch):
    call_count = {"n": 0}

    def fake_call_agent(model, system_prompt, user_prompt, api_key, backend="openrouter"):
        call_count["n"] += 1
        return f"summary #{call_count['n']}"

    monkeypatch.setattr(engine, "call_agent", fake_call_agent)

    config = GameConfig(
        agents=[AgentConfig(name="A", objective="x", model="model-a")],
        judge=JudgeConfig(model="judge-model", context="context"),
        scenario="turn 0 situation",
        num_turns=3,
        openrouter_api_key="fake-key",
    )

    result = engine.run_game(config)
    turns = result.turns

    assert len(turns) == 3
    assert turns[0].situation == "turn 0 situation"
    # each turn's outcome should become the next turn's starting situation
    assert turns[1].situation == turns[0].summary
    assert turns[2].situation == turns[1].summary
    # 1 agent + 1 judge per turn over 3 turns, then one final-summary
    # call — which is the last call made, so its reply is the summary.
    assert call_count["n"] == 7
    assert result.final_summary == "summary #7"


def test_run_game_reports_progress_per_model_call(monkeypatch):
    def fake_call_agent(model, system_prompt, user_prompt, api_key, backend="openrouter"):
        return "reply"

    monkeypatch.setattr(engine, "call_agent", fake_call_agent)

    config = GameConfig(
        agents=[
            AgentConfig(name="A", objective="x", model="model-a"),
            AgentConfig(name="B", objective="y", model="model-b"),
        ],
        judge=JudgeConfig(model="judge-model", context="context"),
        scenario="start",
        num_turns=2,
        openrouter_api_key="fake-key",
    )

    events = []
    engine.run_game(config, on_progress=lambda done, total, label: events.append((done, total, label)))

    # (2 agents + 1 judge) * 2 turns + 1 final summary = 7 calls, one
    # progress event fired right before each, counting up from 0.
    assert engine.total_model_calls(2, 2) == 7
    assert [e[0] for e in events] == list(range(7))
    assert all(e[1] == 7 for e in events)
    assert events[0][2] == "Turn 1: A is deciding"
    assert events[2][2] == "Turn 1: the judge is resolving the turn"
    assert events[-1][2] == "The judge is writing the after-action summary"


def test_run_game_final_summary_sees_the_whole_transcript(monkeypatch):
    # The after-action summary call must receive the starting scenario and
    # every turn's actions/outcomes, and use the judge's summary prompt.
    prompts = []

    def fake_call_agent(model, system_prompt, user_prompt, api_key, backend="openrouter"):
        prompts.append((system_prompt, user_prompt))
        return f"reply #{len(prompts)}"

    monkeypatch.setattr(engine, "call_agent", fake_call_agent)

    config = GameConfig(
        agents=[AgentConfig(name="A", objective="x", model="model-a")],
        judge=JudgeConfig(model="judge-model", context="context"),
        scenario="the opening scenario",
        num_turns=2,
        openrouter_api_key="fake-key",
    )

    engine.run_game(config)

    summary_system, summary_user = prompts[-1]
    assert "simulation that has just ended" in summary_system
    assert "the opening scenario" in summary_user
    assert "Turn 1" in summary_user and "Turn 2" in summary_user
    # agent A's turn-1 action (reply #1) and both turn outcomes appear
    assert "reply #1" in summary_user
    assert "reply #2" in summary_user and "reply #4" in summary_user
