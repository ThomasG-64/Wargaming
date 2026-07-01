# AI-Assisted Wargaming for Animal Welfare

A configurable multi-agent policy wargame backend. You define any number
of stakeholder agents (a name, an objective, and which model plays them),
a judge (a model plus background context to ground its rulings), a
starting scenario, and a turn count — the engine runs the simulation and
returns a judge-adjudicated turn-by-turn transcript. Every model call
goes through [OpenRouter](https://openrouter.ai/), so one API key covers
any model any agent picks.

This is being built as a backend-first project: the goal is a website
where all of the above (agents, judge, scenario, turns, your OpenRouter
key) are just form fields. See `src/wargame/config.py`'s `GameConfig` —
that's the exact object a web request will build and hand to
`engine.run_game()`.

See [docs/research-plan.docx](docs/research-plan.docx) for the original
research background and rationale (note: the project has since pivoted
to a fully user-configurable design rather than the fixed animal-welfare
scenario/agents described there).

## Status

Backend prototype: fully configurable agents/judge/scenario/turn-count,
run via an example script. No web interface yet. See
[the roadmap](#roadmap) below.

## Setup

1. Install Python 3.12+.
2. Create and activate a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate   # Windows
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and add your OpenRouter key
   (get one at https://openrouter.ai/). This key is only read locally
   by the demo script below — the backend itself takes the key as a
   parameter, since a real website passes each visitor's own key per
   request.

## Running the example game

```
venv\Scripts\python.exe scripts/run_example.py
```

Edit `scripts/run_example.py` directly to try your own agents, judge
context, scenario, or turn count — everything in `EXAMPLE_CONFIG` there
is exactly what a website form will eventually collect. Writes a
Markdown transcript to `output/` (gitignored).

## The backend API

```python
from wargame.agents import AgentConfig
from wargame.judge import JudgeConfig
from wargame.config import GameConfig
from wargame.engine import run_game

config = GameConfig(
    agents=[AgentConfig(name="...", objective="...", model="anthropic/claude-3.5-sonnet")],
    judge=JudgeConfig(model="anthropic/claude-3.5-sonnet", context="..."),
    scenario="...",
    num_turns=5,
    openrouter_api_key="...",
)
turns = run_game(config)  # list[TurnRecord]
```

`model` fields are OpenRouter model slugs — browse options at
https://openrouter.ai/models.

## Project layout

```
src/wargame/    importable package: agents, judge, game config, the turn engine, the LLM wrapper
scripts/        entry-point scripts that use the package (run_example.py)
tests/          automated tests (no API key required)
docs/           design docs
output/         generated transcripts (gitignored)
```

## Roadmap

- **Backend prototype** — configurable agents/judge/scenario/turns, OpenRouter-backed, runnable via example script. *(current)*
- **Next** — welfare/outcome-scoring module, structured JSON output (not just Markdown), agent memory across turns.
- **Later** — web frontend calling `GameConfig`/`run_game` directly.
