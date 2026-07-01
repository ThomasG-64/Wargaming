"""GameConfig: the one object that fully describes a game to run.

This is the intended seam between this backend and a future website —
a web route's whole job will be: read form/JSON input, build a
GameConfig, call engine.run_game(config), serialize the result. Nothing
else in this package should need to change when the website is built.
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
