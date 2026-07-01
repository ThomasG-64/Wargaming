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

Runs locally as a website: a form for agents/judge/scenario/turns/your
OpenRouter key, submit, and it runs the whole game and displays the
transcript. See [the roadmap](#roadmap) below for what's not built yet
(deployment, live per-turn progress, etc.).

## Setup

1. Install Python 3.12+.
2. Create and activate a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate   # Windows
   ```
3. Install dependencies and the project itself (editable install, so
   `import wargame` works from anywhere — scripts, tests, the web app):
   ```
   pip install -r requirements.txt
   pip install -e .
   ```
4. Copy `.env.example` to `.env` and add your OpenRouter key
   (get one at https://openrouter.ai/). This is only used by the demo
   script below for local convenience — the website itself has you type
   your key into the page, since a real deployment would have each
   visitor bring their own.

## Running the website (local only, for now)

```
venv\Scripts\python.exe -m uvicorn web.app:app --reload
```

Then open **http://127.0.0.1:8000** in your browser (don't just
double-click `web/static/index.html` — it needs to be served by the
running server, and the page will warn you if it detects it wasn't).
The page loads pre-filled with a full 8-agent example roster, a judge,
and a scenario, so you can try it immediately with just your own
OpenRouter key — every field is editable. It's a "submit and wait"
design for now — the whole game runs before anything appears on the
page, which can take a while for more agents/turns; live per-turn
progress is a possible later upgrade,
not built yet. `web/app.py` is a thin layer over the backend — see
"The backend API" below for what it actually calls.

## Running the example game

```
venv\Scripts\python.exe scripts/run_example.py
```

Edit `scripts/run_example.py` directly to try your own agents, judge
context, scenario, or turn count — everything in `EXAMPLE_CONFIG` there
is exactly what a website form will eventually collect. Writes a
Markdown transcript to `output/` (gitignored).

## The backend API

This is the exact seam a web route will use: parse the request body into
a dict, build a `GameConfig` from it with `from_dict` (plain
`GameConfig(**data)` does *not* work — see the docstring on
`from_dict` for why), run the game, serialize the result.

```python
from dataclasses import asdict
from wargame.config import GameConfig
from wargame.engine import run_game

config = GameConfig.from_dict({
    "agents": [
        {"name": "...", "objective": "...", "model": "anthropic/claude-3.5-sonnet"},
    ],
    "judge": {"model": "anthropic/claude-3.5-sonnet", "context": "..."},
    "scenario": "...",
    "num_turns": 5,
    "openrouter_api_key": "...",
})

turns = run_game(config)               # raises ValueError with a specific,
                                        # user-facing message if input is invalid
turns_json = [asdict(t) for t in turns]  # plain JSON-serializable dicts
```

`model` fields are OpenRouter model slugs — browse options at
https://openrouter.ai/models.

## Testing without a live API key

Every module, including the FastAPI HTTP layer, has been verified
end-to-end without spending any real API calls, using litellm's own
`mock_response` feature (it lets a real `litellm.completion()` call run
through its normal request-building path and return a scripted reply
instead of hitting the network) — see `tests/test_llm.py`,
`tests/test_integration.py`, and `tests/test_api.py` (the latter uses
FastAPI's `TestClient` to drive real HTTP requests against the app
in-process). This confirms OpenRouter routing, request shape, the full
multi-agent/multi-turn loop, and the web API all work correctly; the
only thing untested is an actual live model reply, which needs a real
key. Run everything with:

```
venv\Scripts\python.exe -m pytest tests/ -v
```

## Project layout

```
src/wargame/    importable package: agents, judge, game config, the turn engine, the LLM wrapper
web/            FastAPI backend (app.py) + the browser frontend (static/index.html)
scripts/        entry-point scripts that use the package (run_example.py)
tests/          automated tests (no API key required)
docs/           design docs
output/         generated transcripts (gitignored)
```

## Roadmap

- **Website (local only)** — form-driven agents/judge/scenario/turns, OpenRouter-backed, submit-and-wait results. *(current)*
- **Next** — a real live-key run-through together, then decide what's worth adding: live per-turn progress, deploying it somewhere reachable, welfare/outcome-scoring module, structured JSON output beyond the raw transcript, agent memory across turns.
