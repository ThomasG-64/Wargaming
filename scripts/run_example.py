"""Run one example game through the backend.

This is *one example* configuration, not "the" scenario — everything
here (agents, judge context, scenario, turn count) is exactly the kind
of thing a future website form would collect instead. Edit the values
below freely to try your own game.

Usage:
    venv/Scripts/python.exe scripts/run_example.py
"""

import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# Let this script import the `wargame` package from src/ without installing it.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from dotenv import load_dotenv

from wargame.agents import AgentConfig
from wargame.config import GameConfig
from wargame.engine import run_game
from wargame.judge import JudgeConfig

# load_dotenv() is a convenience for running this demo script locally —
# it reads OPENROUTER_API_KEY out of your .env file. A real backend
# serving a website would instead receive each visitor's key as part of
# the incoming request and pass it straight into GameConfig, never
# touching a local .env at all.
load_dotenv()

EXAMPLE_CONFIG = GameConfig(
    agents=[
        AgentConfig(
            name="Poultry Integrator",
            objective=(
                "Maximize profit margin and market share. Minimize regulatory "
                "compliance cost. Adopt AI tools that cut cost-per-pound, resist "
                "oversight that raises costs without raising revenue."
            ),
            model="anthropic/claude-3.5-sonnet",
        ),
        AgentConfig(
            name="Regulator",
            objective=(
                "Protect food security and political stability. Maintain voter "
                "satisfaction. Show nominal welfare compliance without imposing "
                "costs that destabilize the food supply chain."
            ),
            model="openai/gpt-4o",
        ),
        AgentConfig(
            name="Animal Welfare NGO",
            objective=(
                "Win measurable welfare improvements and legislative change. "
                "Build public awareness and pressure industry and regulators "
                "through campaigns, lobbying, and media."
            ),
            model="anthropic/claude-3.5-sonnet",
        ),
    ],
    judge=JudgeConfig(
        model="anthropic/claude-3.5-sonnet",
        context=(
            "This is a policy wargame about AI's growing role in animal "
            "agriculture. Roughly 80 billion land animals are raised for food "
            "annually, mostly in industrial confinement systems. AI-driven "
            "precision livestock farming is a real, fast-growing market, and "
            "regulators currently have no established framework for "
            "evaluating AI-driven changes to farm operations."
        ),
    ),
    scenario=(
        "A major poultry integrator has deployed an AI system that "
        "autonomously adjusts stocking density, lighting schedules, and feed "
        "formulation in real time to minimize cost-per-pound across its "
        "broiler chicken operations. The system has been live for three "
        "months. Early production data shows a 4% reduction in "
        "cost-per-pound. An animal welfare NGO has just published a report "
        "raising questions about what the AI's optimization actually "
        "optimized for, and whether anyone outside the company can verify it."
    ),
    num_turns=5,
    openrouter_api_key=os.environ.get("OPENROUTER_API_KEY", ""),
)


def write_transcript(turns, output_path: Path) -> None:
    lines = ["# Example game — simulation transcript\n"]
    for turn in turns:
        lines.append(f"## Turn {turn.turn_number}\n")
        lines.append(f"**Situation:** {turn.situation}\n")
        for agent_name, action in turn.actions.items():
            lines.append(f"**{agent_name}:** {action}\n")
        lines.append(f"**Outcome:** {turn.summary}\n")
    output_path.write_text("\n".join(lines), encoding="utf-8")


def main():
    if not EXAMPLE_CONFIG.openrouter_api_key:
        raise SystemExit(
            "No OPENROUTER_API_KEY found. Copy .env.example to .env and add your key."
        )

    print(f"Running example game with {len(EXAMPLE_CONFIG.agents)} agents for {EXAMPLE_CONFIG.num_turns} turns...")
    turns = run_game(EXAMPLE_CONFIG)

    output_dir = Path(__file__).resolve().parent.parent / "output"
    output_dir.mkdir(exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    output_path = output_dir / f"transcript-{timestamp}.md"
    write_transcript(turns, output_path)

    print(f"Done. Transcript written to {output_path}")


if __name__ == "__main__":
    main()
