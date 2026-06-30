"""Stakeholder agent definitions.

Each Agent is just data: a name, what they care about, and which model
plays them. The engine (engine.py) is what actually calls the LLM using
this data — keeping the data and the behavior separate makes it easy to
add a 4th, 5th, 6th agent later without touching the turn loop at all.
"""

from dataclasses import dataclass

DEFAULT_MODEL = "claude-sonnet-4-5-20250929"


@dataclass
class Agent:
    name: str
    objective: str
    system_prompt: str
    model: str = DEFAULT_MODEL


def make_agent(name: str, role_description: str, objective: str, model: str = DEFAULT_MODEL) -> Agent:
    system_prompt = (
        f"You are role-playing as {role_description} in a policy wargame "
        f"about AI's growing role in animal agriculture.\n\n"
        f"Your objective: {objective}\n\n"
        f"Stay in character. Respond with concrete, realistic actions this "
        f"actor would actually take given the situation you're shown — not "
        f"a list of options, not a balanced overview. Be specific: name the "
        f"action, who it targets, and what outcome you're hoping for. "
        f"Keep your response to 2-4 sentences."
    )
    return Agent(name=name, objective=objective, system_prompt=system_prompt, model=model)


INTEGRATOR = make_agent(
    name="Poultry Integrator",
    role_description="a large industrial poultry integrator (like JBS or Tyson)",
    objective=(
        "Maximize profit margin and market share. Minimize regulatory "
        "compliance cost. Adopt AI tools that cut cost-per-pound, "
        "resist oversight that raises costs without raising revenue."
    ),
)

REGULATOR = make_agent(
    name="Regulator",
    role_description="a national food/agriculture regulatory body (like the USDA)",
    objective=(
        "Protect food security and political stability. Maintain voter "
        "satisfaction. Show nominal welfare compliance without imposing "
        "costs that destabilize the food supply chain."
    ),
)

WELFARE_NGO = make_agent(
    name="Animal Welfare NGO",
    role_description="an animal welfare advocacy NGO",
    objective=(
        "Win measurable welfare improvements and legislative change. "
        "Build public awareness and pressure industry and regulators "
        "through campaigns, lobbying, and media."
    ),
)

# To try a different model on one agent, e.g. for cross-model comparison:
#   REGULATOR = make_agent(..., model="gpt-5")
# litellm picks the right provider/API key automatically from this string.
STARTER_AGENTS = [INTEGRATOR, REGULATOR, WELFARE_NGO]
