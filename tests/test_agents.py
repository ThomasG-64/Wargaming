"""Confirms the exact name/objective text passed in ends up verbatim in
the generated system prompt - this is what actually gets sent to the
model, so a bug here would silently ignore whatever the website/user
typed in."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from wargame.agents import build_agent_system_prompt


def test_name_and_objective_appear_verbatim_in_the_prompt():
    prompt = build_agent_system_prompt(
        name="Totally Custom Agent Name",
        objective="A very specific objective the user typed into the form.",
    )
    assert "Totally Custom Agent Name" in prompt
    assert "A very specific objective the user typed into the form." in prompt


def test_different_agents_get_different_prompts():
    prompt_a = build_agent_system_prompt(name="Agent A", objective="Do X")
    prompt_b = build_agent_system_prompt(name="Agent B", objective="Do Y")
    assert prompt_a != prompt_b
    assert "Agent A" not in prompt_b
    assert "Do X" not in prompt_b
