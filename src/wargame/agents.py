"""Agent configuration and system-prompt building.

An AgentConfig is pure user-supplied data — name, objective, and which
model plays them — with nothing hardcoded about who the agents actually
are. A website form produces a list of these directly; the engine
(engine.py) is what calls the LLM using this data.
"""

from dataclasses import dataclass


@dataclass
class AgentConfig:
    name: str       # user-supplied label, e.g. "Poultry Integrator" — shown in transcripts
    objective: str  # user-supplied free text describing what this agent wants
    model: str      # OpenRouter model slug, e.g. "anthropic/claude-3.5-sonnet"


def build_agent_system_prompt(name: str, objective: str) -> str:
    """Build the system prompt for one agent's turn.

    Only the "You are ..." and "Your objective: ..." lines below come
    from user-supplied data (name, objective). Everything after that is
    fixed behavioral instruction that applies to every agent regardless
    of what the user typed as their objective.
    """
    return (
        f"You are role-playing as {name} in a multi-stakeholder wargame "
        f"simulation.\n\n"
        f"Your objective: {objective}\n\n"
        # EDIT HERE: this is the part to tune if agent responses come back
        # too vague, too long, too wishy-washy, or formatted wrong. It has
        # nothing to do with any specific agent's objective, so changing
        # it changes behavior for every agent at once.
        f"Stay in character. Respond with the concrete, realistic actions "
        f"this actor would actually take given the situation you're shown "
        f"— not a list of options, not a balanced overview. For each "
        f"action, be specific about what you do, who it targets, how you "
        f"execute it (the channel, the ask, the resources committed), and "
        f"what outcome you're hoping for. Where it matters, distinguish "
        f"your public moves from your private maneuvering. Write 1-3 "
        f"substantial paragraphs (roughly 150-300 words) — enough detail "
        f"that a judge could realistically adjudicate whether each action "
        f"works, but no filler or restating of the situation."
    )
