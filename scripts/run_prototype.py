"""Run the Week 1 prototype: 3 agents, 1 scenario, 5 turns.

Usage:
    venv/Scripts/python.exe scripts/run_prototype.py
"""

import sys
from datetime import datetime, timezone
from pathlib import Path

# Let this script import the `wargame` package from src/ without installing it.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from dotenv import load_dotenv

from wargame.agents import STARTER_AGENTS
from wargame.engine import run_simulation
from wargame.scenarios import THE_OPTIMIZER

load_dotenv()


def write_transcript(turns, output_path: Path) -> None:
    lines = [f"# {THE_OPTIMIZER.name} — simulation transcript\n"]
    for turn in turns:
        lines.append(f"## Turn {turn.turn_number}\n")
        lines.append(f"**Situation:** {turn.situation}\n")
        for agent_name, action in turn.actions.items():
            lines.append(f"**{agent_name}:** {action}\n")
        lines.append(f"**Outcome:** {turn.summary}\n")
    output_path.write_text("\n".join(lines), encoding="utf-8")


def main():
    print(f"Running '{THE_OPTIMIZER.name}' with {len(STARTER_AGENTS)} agents for 5 turns...")
    turns = run_simulation(THE_OPTIMIZER, STARTER_AGENTS, num_turns=5)

    output_dir = Path(__file__).resolve().parent.parent / "output"
    output_dir.mkdir(exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    output_path = output_dir / f"transcript-{timestamp}.md"
    write_transcript(turns, output_path)

    print(f"Done. Transcript written to {output_path}")


if __name__ == "__main__":
    main()
