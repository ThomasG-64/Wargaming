"""The turn loop: each agent privately decides an action, the judge
resolves all actions into an outcome, and that outcome becomes the next
turn's starting situation.
"""

from dataclasses import dataclass, field

from wargame.agents import AgentConfig, build_agent_system_prompt
from wargame.config import GameConfig
from wargame.judge import JudgeConfig, build_judge_final_summary_prompt, build_judge_system_prompt
from wargame.llm import call_agent


@dataclass
class TurnRecord:
    turn_number: int
    situation: str
    actions: dict = field(default_factory=dict)  # agent name -> action text
    summary: str = ""


@dataclass
class GameResult:
    """Everything a finished game produces: the per-turn records plus the
    judge's one-off after-action summary of the whole game (written by
    the judge model from the full transcript, once the last turn is
    resolved — see build_judge_final_summary_prompt for its shape)."""
    turns: list[TurnRecord]
    final_summary: str


def run_turn(
    turn_number: int,
    situation: str,
    agents: list[AgentConfig],
    judge: JudgeConfig,
    api_key: str,
    backend: str = "openrouter",
    on_call: "callable | None" = None,
) -> TurnRecord:
    """Run one turn. `on_call(label)`, if given, is invoked right before
    each model call with a human-readable description of it — the hook
    the website's progress display hangs off."""
    record = TurnRecord(turn_number=turn_number, situation=situation)

    # Each agent privately decides what they do this turn.
    for agent in agents:
        if on_call:
            on_call(f"Turn {turn_number}: {agent.name} is deciding")
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
            backend=backend,
        )
        record.actions[agent.name] = action

    # The judge resolves all actions into what happens next.
    if on_call:
        on_call(f"Turn {turn_number}: the judge is resolving the turn")
    actions_block = "\n\n".join(f"{name}:\n{action}" for name, action in record.actions.items())
    record.summary = call_agent(
        model=judge.model,
        system_prompt=build_judge_system_prompt(judge.context),
        user_prompt=(
            f"Situation at the start of this turn:\n{situation}\n\n"
            f"Actions taken this turn:\n{actions_block}"
        ),
        api_key=api_key,
        backend=backend,
    )
    return record


def build_transcript_text(scenario: str, turns: list[TurnRecord]) -> str:
    """The full game as one plain-text document — the user message for the
    judge's final-summary call (and a decent human-readable transcript)."""
    parts = [f"Starting scenario:\n{scenario}"]
    for turn in turns:
        actions_block = "\n\n".join(f"{name}:\n{action}" for name, action in turn.actions.items())
        parts.append(f"=== Turn {turn.turn_number} ===\n\n{actions_block}\n\nOutcome:\n{turn.summary}")
    return "\n\n".join(parts)


def total_model_calls(num_agents: int, num_turns: int) -> int:
    """How many model calls a full game makes: every agent once per turn,
    the judge once per turn, plus the one final-summary call. The one
    number progress reporting is measured against."""
    return num_turns * (num_agents + 1) + 1


def run_game(config: GameConfig, on_progress: "callable | None" = None) -> GameResult:
    """Run the whole game. `on_progress(completed, total, label)`, if
    given, is invoked right before each model call: `completed` calls have
    finished out of `total`, and `label` says what's happening now."""
    config.validate()  # fail fast with a clear message before spending any API calls

    total = total_model_calls(len(config.agents), config.num_turns)
    started = 0

    def note(label: str) -> None:
        nonlocal started
        # Called right before a model call, so calls completed == calls
        # started before this one.
        if on_progress:
            on_progress(started, total, label)
        started += 1

    turns = []
    situation = config.scenario
    for turn_number in range(1, config.num_turns + 1):
        record = run_turn(
            turn_number, situation, config.agents, config.judge,
            config.openrouter_api_key, backend=config.backend,
            on_call=note,
        )
        turns.append(record)
        situation = record.summary  # this turn's outcome is next turn's starting situation

    # One extra judge call at the end: the after-action summary of the
    # whole game, from the full transcript. Same judge model and context
    # as turn adjudication, different fixed instructions.
    note("The judge is writing the after-action summary")
    final_summary = call_agent(
        model=config.judge.model,
        system_prompt=build_judge_final_summary_prompt(config.judge.context),
        user_prompt=build_transcript_text(config.scenario, turns),
        api_key=config.openrouter_api_key,
        backend=config.backend,
    )
    return GameResult(turns=turns, final_summary=final_summary)
