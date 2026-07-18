"""Judge configuration and system-prompt building.

The judge is not an agent — it has no objective or side. It's the
neutral adjudicator that resolves what every agent's actions actually
add up to each turn. It gets `context` instead of an objective:
factual background that grounds its rulings in reality. In practice
that's always the shared library in judge_context.py (real cases,
events, and trends about animal welfare and agriculture); the field
stays free-form so custom runs can override it.
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
        f"what happens as a result: which actions succeed, which fail or "
        f"backfire and why, how the actions interact with each other, "
        f"what unintended consequences emerge, and how the overall "
        f"situation has changed. Address every stakeholder's move — don't "
        f"let anyone's action silently disappear. Pace outcomes "
        f"realistically: regulatory decisions, lawsuits, and legislative "
        f"fights take multiple turns to resolve, not one — a single "
        f"turn's actions should move the needle, not settle the fight. "
        f"You may introduce plausible outside shocks (disease outbreaks, "
        f"undercover investigations, price spikes) if the agents' actions "
        f"don't create enough tension on their own. If the starting "
        f"scenario adds its own premises — technological shifts, new "
        f"laws, market shocks — take them as given rather than disputing "
        f"them, and adjudicate from realistic stakeholder incentives "
        f"within them. Write 2-3 paragraphs (roughly 200-350 words) as a "
        f"news-style situation update that will be shown to all players "
        f"as the start of the next turn. Be concrete and specific, not "
        f"vague."
    )


def build_judge_final_summary_prompt(context: str) -> str:
    """System prompt for the judge's one extra call after the last turn:
    an after-action summary of the whole game.

    The engine sends the full transcript (starting scenario + every
    turn's actions and outcome) as the user message; this prompt controls
    what the summary looks like. Only the "Background context" line is
    per-game data (the same fixed context the turn judge gets).
    """
    context_block = context.strip() if context.strip() else "(no additional context provided)"
    return (
        f"You are the neutral judge of a multi-stakeholder wargame "
        f"simulation that has just ended.\n\n"
        f"Background context to ground your analysis in reality:\n{context_block}\n\n"
        # EDIT HERE: this is the part to tune if final summaries come back
        # too long/short, too vague, wrongly formatted, or focused on the
        # wrong things. The three-part shape below is what the website
        # renders under "What happened".
        f"You will be shown the full game transcript: the starting "
        f"scenario and, for each turn, every stakeholder's actions and "
        f"the resolved outcome. Write an after-action report in exactly "
        f"this shape:\n"
        f"1. An opening paragraph (5-8 sentences) telling the story of "
        f"the game: where things started, the pivotal developments that "
        f"defined it, and where things ended up.\n"
        f"2. Then 4-8 bullet points (each 1-2 sentences, starting with "
        f"\"- \") covering the consequential developments, ordered by how "
        f"much they mattered — NOT by when they happened. Structural "
        f"changes lead (laws or rules enacted, systems abolished or "
        f"entrenched, major commitments made or broken, markets or "
        f"coalitions durably shifted); a major turning point belongs at "
        f"the top even if it happened late, and routine maneuvering that "
        f"never changed the trajectory should be left out entirely, even "
        f"from early turns.\n"
        f"3. A closing paragraph (3-5 sentences) starting exactly with "
        f"\"Implications for animal welfare:\" — what this game suggests "
        f"about how animal welfare actually fares under this kind of "
        f"scenario: who or what actually moved welfare outcomes, which "
        f"levers worked, which failed, and what that suggests going "
        f"forward. Stated plainly.\n\n"
        f"Do not give the report a title or markdown headings — start "
        f"directly with the opening paragraph. Do not recap turn-by-turn "
        f"— the reader can open the per-turn outcomes separately; your "
        f"job is judgment about what mattered. Do not mention the "
        f"simulation's mechanics (turns, agents, judging) — write like a "
        f"news analyst's retrospective. Be concrete: name the "
        f"stakeholders and what they actually did, not generic labels "
        f"like 'various parties'."
    )
