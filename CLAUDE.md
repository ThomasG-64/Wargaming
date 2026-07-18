# WargamingLLM — project notes for Claude Code

A multi-agent LLM policy wargame about animal welfare: stakeholder
agents (each played by a model) act each turn, a judge model resolves
outcomes, and after the last turn the judge writes an after-action
summary. Served as a local website (FastAPI + one static page).

## Architecture (read in this order)

- `src/wargame/llm.py` — the ONLY place model calls happen. Two backends
  behind one `call_agent()`: `"openrouter"` (litellm, visitor-supplied
  key) and `"claude_code"` (Claude Agent SDK driving the local Claude
  Code CLI: tool-less, single-turn, hermetic, API keys blanked in the
  subprocess).
- `src/wargame/agents.py`, `judge.py` — system-prompt builders. The
  tunable fixed instructions are marked `EDIT HERE`. The judge has two
  prompts: per-turn adjudication and the final after-action summary.
- `src/wargame/judge_context.py` — the judge's factual "precedent
  library" (attempt → outcome → why), shared by every game.
- `src/wargame/engine.py` — the turn loop. `run_game(config,
  on_progress)` returns a `GameResult` (turns + final_summary);
  `on_progress(completed, total, label)` fires before each model call
  and powers the website's progress ring.
- `src/wargame/config.py` — `GameConfig`, built via `from_dict()` (NOT
  the constructor — see its docstring), validated with `validate()`.
- `src/wargame/presets.py` — SINGLE SOURCE OF TRUTH for all website
  content: the 8-agent roster (`AGENT_LIBRARY`), scenario presets,
  fixed judge context, curated model menus, and defaults. The page
  hardcodes none of it; `website_prefill()` serves it all at
  GET /api/presets. Edit content here, never in the HTML.
- `web/app.py` — thin HTTP layer. Runs are BACKGROUND JOBS: POST
  /api/run validates then returns a job id; the page polls GET
  /api/run/{id}. Finished runs append to `output/runs.jsonl`
  (gitignored) and GET /api/runs serves them all — that's why the
  Results tab is permanent across reloads. Failed runs are NOT saved.
- `web/static/index.html` — the whole frontend (vanilla JS, one file):
  roster picker + custom agents, scenario dropdown + custom option,
  per-backend model dropdowns, progress ring, Results renderer,
  Implications article (placeholder awaiting cross-run analysis).

## Website invariants (enforced server-side, don't relax casually)

- Roster agents are submitted by NAME only; objectives resolve from
  `AGENT_LIBRARY` and a request-supplied objective for a roster name is
  deliberately ignored. Custom (non-roster) agents must carry their own
  objective.
- Models must come from the active backend's menu in presets.py
  (`OPENROUTER_MODEL_CHOICES` / `CLAUDE_CODE_MODEL_CHOICES`).
- The judge's context is fixed server-side; the website never sends one.

## claude_code backend billing — important

CLI runs bill whatever Claude account the `claude` CLI on this machine
is logged into, UNLESS `CLAUDE_CODE_OAUTH_TOKEN` is set in `.env`
(generated via `claude setup-token` under the intended account). The
server prints which mode it's in at startup. This machine has both a
personal Pro and a work Max login — an unpinned run once silently
drained the personal account's window. Also: a full game is ~31 CLI
calls; concurrent games can exhaust a subscription window mid-run, and
a usage-limit failure kills the run unrecoverably (no partial saves).
Prefer the openrouter backend for batch campaigns.

## Running things

- Dev server: `.claude/launch.json` name `wargame-web` (uvicorn on
  :8000). Use the preview tool, not raw Bash. Restart it after editing
  Python (no --reload).
- Tests: `venv\Scripts\python.exe -m pytest tests -q` — no API key or
  network needed (litellm `mock_response` + a stubbed Agent-SDK
  `query`). Keep it that way: new model-call paths need a mocked seam.
- Demo script: `scripts/run_example.py` (reads OPENROUTER_API_KEY from
  `.env`).

## Conventions

- Fail fast with user-facing ValueError messages via
  `GameConfig.validate()`; the web layer maps them to 400s before any
  model call is spent.
- Prompt-shape changes: tests assert on key phrases of the judge
  summary prompt ("bullet points", "Implications for animal welfare:")
  and progress labels — update `tests/` alongside.
- `docs/redteam.md` is the standing critique of the project's validity
  (single-judge bias, no agent memory, no run-to-run variance). Check
  proposed features against it — run-to-run variance display and
  panel judging are the highest-leverage known gaps.
