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
        f"Stay in character. Respond with concrete, realistic actions this "
        f"actor would actually take given the situation you're shown — not "
        f"a list of options, not a balanced overview. Be specific: name the "
        f"action, who it targets, and what outcome you're hoping for. "
        f"Keep your response to 2-4 sentences."
    )
