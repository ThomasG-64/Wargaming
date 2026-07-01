"""Tests for GameConfig's website-facing seams: building from a JSON-like
dict, validating before running, and serializing results back out."""

import dataclasses
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from wargame.agents import AgentConfig
from wargame.config import GameConfig
from wargame.engine import TurnRecord
from wargame.judge import JudgeConfig


def make_valid_dict():
    return {
        "agents": [
            {"name": "A", "objective": "obj-a", "model": "anthropic/claude-3.5-sonnet"},
            {"name": "B", "objective": "obj-b", "model": "openai/gpt-4o"},
        ],
        "judge": {"model": "anthropic/claude-3.5-sonnet", "context": "background info"},
        "scenario": "something happens",
        "num_turns": 3,
        "openrouter_api_key": "fake-key",
    }


def test_from_dict_builds_real_nested_dataclasses():
    config = GameConfig.from_dict(make_valid_dict())

    assert isinstance(config, GameConfig)
    assert isinstance(config.judge, JudgeConfig)
    assert all(isinstance(a, AgentConfig) for a in config.agents)
    assert config.agents[0].name == "A"
    assert config.judge.context == "background info"


def test_from_dict_then_json_dumps_round_trips_through_asdict():
    # Simulates: website receives JSON -> from_dict -> (later) send results
    # back as JSON. Confirms nothing in the data model breaks plain JSON
    # serialization in either direction.
    config = GameConfig.from_dict(make_valid_dict())
    dumped = json.dumps(dataclasses.asdict(config))
    reloaded = GameConfig.from_dict(json.loads(dumped))
    assert reloaded == config


def test_turn_record_serializes_to_json_directly():
    record = TurnRecord(turn_number=1, situation="s", actions={"A": "did x"}, summary="outcome")
    # No from_dict needed on the way out - asdict + json.dumps just works
    # since TurnRecord has no nested dataclasses, only a plain dict field.
    dumped = json.dumps(dataclasses.asdict(record))
    assert json.loads(dumped)["actions"] == {"A": "did x"}


@pytest.mark.parametrize(
    "mutate, expected_message_fragment",
    [
        (lambda d: d.__setitem__("agents", []), "at least one agent"),
        (lambda d: d["agents"][0].__setitem__("name", "  "), "missing a name"),
        (lambda d: d["agents"][0].__setitem__("objective", ""), "missing an objective"),
        (lambda d: d["agents"][0].__setitem__("model", ""), "missing a model"),
        (lambda d: d["judge"].__setitem__("model", ""), "judge is missing a model"),
        (lambda d: d.__setitem__("scenario", "   "), "scenario is required"),
        (lambda d: d.__setitem__("num_turns", 0), "num_turns must be at least 1"),
        (lambda d: d.__setitem__("openrouter_api_key", ""), "api key is required"),
    ],
)
def test_validate_rejects_bad_input_with_clear_message(mutate, expected_message_fragment):
    data = make_valid_dict()
    mutate(data)
    config = GameConfig.from_dict(data)

    with pytest.raises(ValueError, match=r"(?i)" + expected_message_fragment):
        config.validate()


def test_validate_accepts_good_input():
    config = GameConfig.from_dict(make_valid_dict())
    config.validate()  # should not raise
