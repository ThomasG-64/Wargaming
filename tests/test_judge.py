"""Confirms the judge's user-supplied context ends up verbatim in its
system prompt, and that a blank context degrades gracefully instead of
producing a broken/empty prompt."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from wargame.judge import build_judge_system_prompt


def test_context_appears_verbatim_in_the_prompt():
    prompt = build_judge_system_prompt("Some very specific background info.")
    assert "Some very specific background info." in prompt


def test_blank_context_falls_back_to_placeholder_text():
    for blank in ["", "   ", "\n"]:
        prompt = build_judge_system_prompt(blank)
        assert "(no additional context provided)" in prompt
