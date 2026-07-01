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
    def fake_call_agent(model, system_prompt, user_prompt, api_key):
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

    def fake_call_agent(model, system_prompt, user_prompt, api_key):
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

    turns = engine.run_game(config)

    assert len(turns) == 3
    assert turns[0].situation == "turn 0 situation"
    # each turn's outcome should become the next turn's starting situation
    assert turns[1].situation == turns[0].summary
    assert turns[2].situation == turns[1].summary
