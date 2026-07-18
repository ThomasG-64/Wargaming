"""FastAPI backend for the wargame website.

This is a thin HTTP layer over the wargame package — nothing here
should ever contain simulation logic itself.

Runs are BACKGROUND JOBS, not blocking requests: a game with several
agents and turns takes minutes (especially on the claude_code backend,
where every model call spawns a CLI process), which is far too long to
hold one HTTP request open with zero feedback. POST /api/run validates
everything, starts the game on a worker thread, and returns a job id
immediately; the page then polls GET /api/run/{job_id}, which reports
how many model calls have completed out of how many total (the engine's
on_progress hook), what's happening right now, and — once finished —
the full result.

Every finished run is also appended to a JSONL file on disk
(output/runs.jsonl, gitignored) and served back by GET /api/runs, so
the Results tab shows every run ever made on this machine, not just
this browser session's.
"""

import json
import os
import sys
import threading
import time
import uuid
from dataclasses import asdict
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Load .env from the project root so CLAUDE_CODE_OAUTH_TOKEN (if set)
# reaches the Claude Code CLI subprocesses the claude_code backend
# spawns. That token pins WHICH Claude account gets billed for CLI runs;
# without it, billing goes to whatever account the `claude` CLI on this
# machine happens to be logged into — which is easy to get wrong on a
# machine with both a personal and a work login (observed live: a run
# silently billed a personal Pro account). Generate one with
# `claude setup-token` while signed into the intended account.
load_dotenv(Path(__file__).resolve().parent.parent / ".env")
if os.environ.get("CLAUDE_CODE_OAUTH_TOKEN"):
    print("claude_code billing: pinned to the CLAUDE_CODE_OAUTH_TOKEN account (from .env/environment).")
else:
    print(
        "claude_code billing: NOT pinned — CLI runs bill whatever account `claude` "
        "is logged into on this machine. To pin: `claude setup-token` under the "
        "intended account, then set CLAUDE_CODE_OAUTH_TOKEN in .env.",
        file=sys.stderr,
    )

from wargame.config import GameConfig
from wargame.engine import run_game, total_model_calls
from wargame.presets import (
    AGENT_LIBRARY,
    CLAUDE_CODE_MODEL_CHOICES,
    DEFAULT_JUDGE_CONTEXT,
    OPENROUTER_MODEL_CHOICES,
    SCENARIO_PRESETS,
    website_prefill,
)

app = FastAPI()

# The dropdowns on the page are closed lists, so the server enforces the
# same lists — a request with any other model string gets a 400 instead
# of a confusing provider error mid-game.
_ALLOWED_MODELS = {
    "openrouter": {choice["value"] for choice in OPENROUTER_MODEL_CHOICES},
    "claude_code": {choice["value"] for choice in CLAUDE_CODE_MODEL_CHOICES},
}

# Where finished runs are persisted, one JSON object per line. Lives in
# output/ (already gitignored — it's generated data, same as the demo
# script's transcripts). Tests monkeypatch this to a temp path.
RUNS_PATH = Path(__file__).resolve().parent.parent / "output" / "runs.jsonl"

# In-memory job table for runs in flight (and their terminal states).
# Fine for a local single-process server; a real deployment would need
# real job storage, but a real deployment needs to rethink claude_code
# anyway (see RunGameRequest.backend).
_jobs: dict = {}
_jobs_lock = threading.Lock()
_runs_file_lock = threading.Lock()


@app.middleware("http")
async def no_cache(request, call_next):
    # Without this, browsers can silently serve a stale cached copy of
    # index.html (or the /api/presets prefill it fetches) after we've
    # pushed changes - you'd edit a preset, redeploy, refresh, and still
    # see the old one until a hard-refresh happened to bypass the cache.
    # This is a small personal tool, not a high-traffic site, so
    # trading away caching entirely for "you always see what's actually
    # deployed" is the right default.
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-store, must-revalidate"
    return response


# Agents come in two kinds. Roster agents are picked from the fixed
# library by name, and their objective is resolved server-side from
# wargame.presets.AGENT_LIBRARY — whatever objective the request carries
# for a roster name is ignored, so the researched objectives can't be
# quietly edited. Custom agents (any name NOT in the library) must carry
# their own objective, which is used as-is. The judge's context is
# always DEFAULT_JUDGE_CONTEXT either way.
class AgentSelection(BaseModel):
    name: str
    model: str
    objective: str = ""


class RunGameRequest(BaseModel):
    agents: list[AgentSelection]
    judge_model: str
    scenario: str
    num_turns: int
    # "openrouter" calls models via the visitor's OpenRouter key.
    # "claude_code" runs each call through the Claude Code CLI installed
    # on the machine hosting this server — no key required; billing goes
    # to whatever Claude account that CLI is logged into. Only meaningful
    # while this site runs locally (the CLI is the *server's*, not the
    # visitor's — revisit before deploying anywhere shared).
    backend: Literal["openrouter", "claude_code"] = "openrouter"
    openrouter_api_key: str = ""


def _build_config(request: RunGameRequest) -> GameConfig:
    """Resolve the request into a validated GameConfig, raising
    HTTPException(400) on anything the user got wrong — all before any
    job starts, so bad input fails instantly, never minutes in."""
    allowed_models = _ALLOWED_MODELS[request.backend]

    def check_model(model: str, who: str) -> None:
        if model not in allowed_models:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Model '{model}' (for {who}) isn't one of this site's model options "
                    f"for the {request.backend} backend."
                ),
            )

    check_model(request.judge_model, "the judge")
    agents = []
    for selection in request.agents:
        library_agent = AGENT_LIBRARY.get(selection.name)
        if library_agent is not None:
            name, objective = library_agent.name, library_agent.objective
        elif selection.objective.strip():
            name, objective = selection.name, selection.objective  # custom agent
        else:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Agent '{selection.name}' isn't in the built-in roster and has no "
                    f"objective. Custom agents must include an objective."
                ),
            )
        check_model(selection.model, name)
        agents.append({"name": name, "objective": objective, "model": selection.model})

    config = GameConfig.from_dict(
        {
            "agents": agents,
            "judge": {"model": request.judge_model, "context": DEFAULT_JUDGE_CONTEXT},
            "scenario": request.scenario,
            "num_turns": request.num_turns,
            "backend": request.backend,
            "openrouter_api_key": request.openrouter_api_key,
        }
    )
    try:
        config.validate()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return config


def _persist_run(record: dict) -> None:
    with _runs_file_lock:
        RUNS_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(RUNS_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")


def _run_job(job_id: str, config: GameConfig, request: RunGameRequest) -> None:
    """Worker-thread body: run the game, streaming progress into the job
    table, then persist and mark done (or record the failure)."""
    job = _jobs[job_id]

    def on_progress(completed: int, total: int, label: str) -> None:
        job["completed"] = completed
        job["label"] = label

    try:
        result = run_game(config, on_progress=on_progress)
    except Exception as e:
        job["status"] = "error"
        job["error"] = f"Model call failed: {e}"
        return

    # Label the run with which preset scenario it was (matched by text),
    # or "Custom scenario" — with many runs across scenarios, this is
    # what makes them tellable-apart in the Results tab and groupable in
    # a later cross-run analysis of runs.jsonl.
    scenario_title = next(
        (p.title for p in SCENARIO_PRESETS if p.scenario == request.scenario),
        "Custom scenario",
    )
    record = {
        "id": job_id,
        "finished_at": time.time(),
        "backend": request.backend,
        "num_turns": request.num_turns,
        "judge_model": request.judge_model,
        "agents": [{"name": a.name, "model": a.model} for a in request.agents],
        "scenario": request.scenario,
        "scenario_title": scenario_title,
        "result": asdict(result),
    }
    _persist_run(record)
    job["completed"] = job["total"]
    job["label"] = "Done"
    job["run"] = record
    job["status"] = "done"


# Routes must be declared before the static-file mount below, or the
# mount (which matches everything under "/") would swallow "/api/..."
# before these routes ever get a chance to match.
@app.post("/api/run")
def start_run(request: RunGameRequest):
    config = _build_config(request)  # 400s here, before any job exists

    job_id = uuid.uuid4().hex
    total = total_model_calls(len(config.agents), config.num_turns)
    with _jobs_lock:
        _jobs[job_id] = {
            "status": "running",
            "completed": 0,
            "total": total,
            "label": "Starting",
            "started_at": time.time(),
            "run": None,
            "error": None,
        }
    threading.Thread(target=_run_job, args=(job_id, config, request), daemon=True).start()
    return {"job_id": job_id, "total": total}


@app.get("/api/run/{job_id}")
def run_status(job_id: str):
    job = _jobs.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="No such run.")
    status = {
        "status": job["status"],
        "completed": job["completed"],
        "total": job["total"],
        "label": job["label"],
        "elapsed_s": round(time.time() - job["started_at"], 1),
    }
    if job["status"] == "done":
        status["run"] = job["run"]
    if job["status"] == "error":
        status["error"] = job["error"]
    return status


# Every run ever completed on this machine, oldest first (the page
# renders newest-first). Powers the permanently-populated Results tab.
@app.get("/api/runs")
def list_runs():
    if not RUNS_PATH.exists():
        return []
    runs = []
    with open(RUNS_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            # One corrupt line (e.g. a crash mid-append) must not take
            # every other stored run down with it.
            try:
                runs.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return runs


# The fixed agent library the page's picker offers, plus the default
# game the form loads pre-filled with. Sourced entirely from
# wargame.presets so the website and the Python presets are one and the
# same thing (see website_prefill's docstring).
@app.get("/api/presets")
def presets():
    return website_prefill()


# Serves web/static/index.html at "/" and anything else in that folder.
app.mount("/", StaticFiles(directory=Path(__file__).parent / "static", html=True), name="static")
