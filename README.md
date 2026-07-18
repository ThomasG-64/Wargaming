# AI-Assisted Wargaming for Animal Welfare

A configurable multi-agent policy wargame. On the website you pick
stakeholder agents from a fixed roster of researched roles (each with a
detailed objective you can view but not edit) — or create your own
custom agents with a name and objective you write yourself — choose
which model plays each of them from a curated dropdown, choose a model
for the neutral judge (whose grounding context is built in), pick a
starting scenario from a preset menu (or write your own), and set a
turn count — the engine runs the simulation and returns a
judge-adjudicated turn-by-turn transcript plus the judge's after-action
summary. Model calls run through one of two backends
(pick on the page under "Run models via"):

- **OpenRouter API** (default) — one [OpenRouter](https://openrouter.ai/)
  key covers any model any agent picks.
- **Claude Code CLI** — no API key at all. Calls run through the Claude
  Code CLI installed on this machine via the Claude Agent SDK and are
  billed to whatever Claude account that CLI is logged into (Anthropic
  models only, named like `claude-haiku-4-5` / `claude-sonnet-5` or
  aliases `haiku`/`sonnet`/`opus`). **Billing pin:** on a machine with
  more than one Claude login (e.g. personal + work), the CLI's ambient
  login decides who gets billed — to pin runs to a specific account, run
  `claude setup-token` while signed into that account, put the token in
  `.env` as `CLAUDE_CODE_OAUTH_TOKEN=...`, and restart the server (it
  prints which mode it's in at startup). Each call is a single-turn,
  tool-less CLI run with the wargame's own system prompt — the CLI's
  agentic scaffolding is stripped out (no tools, no `~/.claude`
  settings, `ANTHROPIC_API_KEY` blanked in the subprocess so a key in
  the server's environment can't be silently billed). Noticeably slower
  than the API since every call spawns a CLI process. Only meaningful
  while the site runs locally — the CLI is the *server's*, so revisit
  before deploying anywhere shared.

The Python backend underneath stays fully free-form: `GameConfig` in
`src/wargame/config.py` takes any agents/objectives/judge-context you
build in code (see `scripts/run_example.py`). The fixed roster and the
fixed judge context are a *website* policy, applied in `web/app.py` and
defined in one place, `src/wargame/presets.py`.

See [docs/research-plan.docx](docs/research-plan.docx) for the original
research background and rationale (note: the project has since pivoted
to a fully user-configurable design rather than the fixed animal-welfare
scenario/agents described there).

## Status

Runs locally as a website: add agents from the fixed roster, pick their
models and the judge's model, write a starting scenario, set turns,
paste your OpenRouter key, submit, and it runs the whole game and
displays the transcript. See [the roadmap](#roadmap) below for what's not built yet
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
The page loads with a ready-to-run lineup of agents and a matching
example scenario, so you can try it immediately with just your own
OpenRouter key. Agents are picked from a fixed 8-role roster (click
"+ Add agent" to browse it and view each role's objective before
adding) or created from scratch in the same picker (your own name +
objective); the starting scenario is picked from a preset menu (or
written from scratch via its "Custom" option). Roster objectives, the
scenario presets, the model menus, and the judge's grounding context
are all fixed in `src/wargame/presets.py`; everything else (which
agents, their models, the judge's model, the scenario, the turn count)
is yours to change on the page. It's a "submit and wait"
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
    # "openrouter" (default, needs the key below) or "claude_code" (the
    # local Claude Code CLI login — no key; Anthropic model ids/aliases).
    "backend": "openrouter",
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

- **Website (local only)** — roster-picked agents, per-agent + judge model choice, free-form scenario/turns, OpenRouter-backed, submit-and-wait results. *(current)*
- **Next** — a real live-key run-through together, then decide what's worth adding: live per-turn progress, deploying it somewhere reachable, welfare/outcome-scoring module, structured JSON output beyond the raw transcript, agent memory across turns.
