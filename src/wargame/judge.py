"""Judge configuration and system-prompt building.

The judge is not an agent — it has no objective or side. It's the
neutral adjudicator that resolves what every agent's actions actually
add up to each turn. It gets `context` instead of an objective: whatever
background information the user thinks it needs to make its rulings
realistic (e.g. relevant regulations, market conditions, prior history).
"""

from dataclasses import dataclass


@dataclass
class JudgeConfig:
    model: str      # OpenRouter model slug
    context: str    # user-supplied background info to ground adjudication in reality


def build_judge_system_prompt(context: str) -> str:
    """Build the judge's system prompt.

    Only the "Background context" line below is user-supplied. Everything
    else is fixed instruction on how to adjudicate, independent of the
    specific game being run.
    """
    context_block = context.strip() if context.strip() else "(no additional context provided)"
    return (
        f"You are the neutral judge of a multi-stakeholder wargame "
        f"simulation.\n\n"
        f"Background context to ground your rulings in reality:\n{context_block}\n\n"
        # EDIT HERE: this is the part to tune if outcomes feel too vague,
        # too harsh/lenient toward one side, or the wrong length/format.
        # It applies to every game regardless of what context was supplied.
        f"You are given the situation at the start of this turn and the "
        f"actions every stakeholder just took. Determine realistically "
        f"what happens as a result: who succeeds, who doesn't, what "
        f"unintended consequences emerge, and how the situation has "
        f"changed. Write 1 short paragraph as a news-style situation "
        f"update that will be shown to all players as the start of the "
        f"next turn. Be concrete and specific, not vague."
    )
