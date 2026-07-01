"""FastAPI backend for the wargame website.

This is a thin HTTP layer over the wargame package — nothing here
should ever contain simulation logic itself. Its whole job: parse the
request body, build a GameConfig, call run_game(), return JSON.
"""

from dataclasses import asdict
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from wargame.config import GameConfig
from wargame.engine import run_game

app = FastAPI()


class AgentInput(BaseModel):
    name: str
    objective: str
    model: str


class JudgeInput(BaseModel):
    model: str
    context: str


class RunGameRequest(BaseModel):
    agents: list[AgentInput]
    judge: JudgeInput
    scenario: str
    num_turns: int
    openrouter_api_key: str


# Routes must be declared before the static-file mount below, or the
# mount (which matches everything under "/") would swallow "/api/run"
# before this route ever gets a chance to match it.
@app.post("/api/run")
def run(request: RunGameRequest):
    config = GameConfig.from_dict(request.model_dump())
    try:
        turns = run_game(config)
    except ValueError as e:
        # config.validate() failures - bad input, the user's fault, 400.
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # EDIT HERE: litellm raises different exception types for bad
        # keys, rate limits, unknown model slugs, etc. For now every
        # failure just surfaces its raw message; consider mapping
        # specific error types to friendlier text once you've seen what
        # actually goes wrong in practice.
        raise HTTPException(status_code=502, detail=f"Model call failed: {e}")

    return [asdict(turn) for turn in turns]


# Serves web/static/index.html at "/" and anything else in that folder.
app.mount("/", StaticFiles(directory=Path(__file__).parent / "static", html=True), name="static")
