"""GameConfig: the one object that fully describes a game to run.

This is the intended seam between this backend and a future website —
a web route's whole job will be: read form/JSON input, build a
GameConfig (via GameConfig.from_dict), call engine.run_game(config),
serialize the result with dataclasses.asdict(). Nothing else in this
package should need to change when the website is built.
"""

from dataclasses import dataclass

from wargame.agents import AgentConfig
from wargame.judge import JudgeConfig


@dataclass
class GameConfig:
    agents: list[AgentConfig]
    judge: JudgeConfig
    scenario: str            # starting situation, plain text
    num_turns: int
    openrouter_api_key: str

    @classmethod
    def from_dict(cls, data: dict) -> "GameConfig":
        """Build a GameConfig from plain nested dicts/lists — the shape a
        website's parsed JSON body actually arrives in.

        Doing `GameConfig(**data)` directly does NOT work correctly: it
        happily constructs a GameConfig, but `agents` ends up as a list of
        plain dicts (not AgentConfig instances) and `judge` as a plain
        dict (not a JudgeConfig instance), since dataclasses don't
        recursively convert nested data on their own. That breaks later,
        deep inside a turn (e.g. `agent.name` raising AttributeError on a
        dict), likely after already spending real API calls on earlier
        agents. Always build from a dict via this method, not the
        constructor directly.
        """
        return cls(
            agents=[AgentConfig(**agent) for agent in data["agents"]],
            judge=JudgeConfig(**data["judge"]),
            scenario=data["scenario"],
            num_turns=data["num_turns"],
            openrouter_api_key=data["openrouter_api_key"],
        )

    def validate(self) -> None:
        """Raise ValueError with a specific, user-facing message on the
        first problem found. Call this before running anything — the
        whole point is failing fast with a message a website can show
        directly, instead of a game partway running before something
        breaks.
        """
        if not self.agents:
            raise ValueError("At least one agent is required.")
        for i, agent in enumerate(self.agents):
            if not agent.name.strip():
                raise ValueError(f"Agent {i + 1} is missing a name.")
            if not agent.objective.strip():
                raise ValueError(f"Agent '{agent.name}' is missing an objective.")
            if not agent.model.strip():
                raise ValueError(f"Agent '{agent.name}' is missing a model.")
        if not self.judge.model.strip():
            raise ValueError("The judge is missing a model.")
        if not self.scenario.strip():
            raise ValueError("A starting scenario is required.")
        if self.num_turns < 1:
            raise ValueError("num_turns must be at least 1.")
        if not self.openrouter_api_key.strip():
            raise ValueError("An OpenRouter API key is required.")
