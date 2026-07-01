"""The turn loop: each agent privately decides an action, the judge
resolves all actions into an outcome, and that outcome becomes the next
turn's starting situation.
"""

from dataclasses import dataclass, field

from wargame.agents import AgentConfig, build_agent_system_prompt
from wargame.config import GameConfig
from wargame.judge import JudgeConfig, build_judge_system_prompt
from wargame.llm import call_agent


@dataclass
class TurnRecord:
    turn_number: int
    situation: str
    actions: dict = field(default_factory=dict)  # agent name -> action text
    summary: str = ""


def run_turn(
    turn_number: int,
    situation: str,
    agents: list[AgentConfig],
    judge: JudgeConfig,
    api_key: str,
) -> TurnRecord:
    record = TurnRecord(turn_number=turn_number, situation=situation)

    # Each agent privately decides what they do this turn.
    for agent in agents:
        # EDIT HERE: this is the fixed instruction each agent is given
        # every turn, independent of their objective — tune if you want
        # them asked for more/fewer actions, more detail, etc.
        action = call_agent(
            model=agent.model,
            system_prompt=build_agent_system_prompt(agent.name, agent.objective),
            user_prompt=(
                f"Current situation:\n{situation}\n\n"
                f"What do you do this turn? Give 1-3 concrete actions."
            ),
            api_key=api_key,
        )
        record.actions[agent.name] = action

    # The judge resolves all actions into what happens next.
    actions_block = "\n\n".join(f"{name}:\n{action}" for name, action in record.actions.items())
    record.summary = call_agent(
        model=judge.model,
        system_prompt=build_judge_system_prompt(judge.context),
        user_prompt=(
            f"Situation at the start of this turn:\n{situation}\n\n"
            f"Actions taken this turn:\n{actions_block}"
        ),
        api_key=api_key,
    )
    return record


def run_game(config: GameConfig) -> list[TurnRecord]:
    turns = []
    situation = config.scenario
    for turn_number in range(1, config.num_turns + 1):
        record = run_turn(turn_number, situation, config.agents, config.judge, config.openrouter_api_key)
        turns.append(record)
        situation = record.summary  # this turn's outcome is next turn's starting situation
    return turns
