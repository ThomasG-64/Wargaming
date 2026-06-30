"""The turn loop. This is a simplified version of the doc's 6-step turn
structure (situation update -> private deliberation -> actions submitted
-> adjudication -> welfare assessment -> turn summary):

For the prototype, we merge "deliberation" and "actions submitted" into
one call per agent (they just tell us what they'd do), and merge
"adjudication" and "turn summary" into one call to a referee agent.
Welfare scoring isn't built yet (Week 2) — for now the summary is purely
narrative.
"""

from dataclasses import dataclass, field

from wargame.agents import Agent, DEFAULT_MODEL
from wargame.llm import call_agent
from wargame.scenarios import Scenario

REFEREE_SYSTEM_PROMPT = (
    "You are the neutral adjudicator of a policy wargame. You are given "
    "the current situation and the actions each stakeholder just took. "
    "Determine realistically what happens as a result: who succeeds, who "
    "doesn't, what unintended consequences emerge, and how the situation "
    "has changed. Write 1 short paragraph as a news-style situation "
    "update that will be shown to all players as the start of the next "
    "turn. Be concrete and specific, not vague."
)


@dataclass
class TurnRecord:
    turn_number: int
    situation: str
    actions: dict = field(default_factory=dict)  # agent name -> action text
    summary: str = ""


def run_turn(turn_number: int, situation: str, agents: list[Agent], referee_model: str = DEFAULT_MODEL) -> TurnRecord:
    record = TurnRecord(turn_number=turn_number, situation=situation)

    # Each agent privately decides what they do this turn.
    for agent in agents:
        action = call_agent(
            model=agent.model,
            system_prompt=agent.system_prompt,
            user_prompt=(
                f"Current situation:\n{situation}\n\n"
                f"What do you do this turn? Give 1-3 concrete actions."
            ),
        )
        record.actions[agent.name] = action

    # The referee resolves all actions into what happens next.
    actions_block = "\n\n".join(f"{name}:\n{action}" for name, action in record.actions.items())
    record.summary = call_agent(
        model=referee_model,
        system_prompt=REFEREE_SYSTEM_PROMPT,
        user_prompt=(
            f"Situation at the start of this turn:\n{situation}\n\n"
            f"Actions taken this turn:\n{actions_block}"
        ),
    )
    return record


def run_simulation(scenario: Scenario, agents: list[Agent], num_turns: int = 5) -> list[TurnRecord]:
    turns = []
    situation = scenario.opening_situation
    for turn_number in range(1, num_turns + 1):
        record = run_turn(turn_number, situation, agents)
        turns.append(record)
        situation = record.summary  # this turn's outcome is next turn's starting situation
    return turns
