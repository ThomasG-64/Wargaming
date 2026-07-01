"""Tests for the FastAPI HTTP layer (web/app.py) — confirms a real HTTP
request/response round-trip works, on top of the already-tested backend
logic. Uses FastAPI's TestClient (no real network port needed) and
litellm's mock_response feature (no real API key needed)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "web"))

import litellm
from fastapi.testclient import TestClient

from app import app

client = TestClient(app)


def make_valid_payload():
    return {
        "agents": [
            {"name": "A", "objective": "obj-a", "model": "anthropic/claude-3.5-sonnet"},
        ],
        "judge": {"model": "anthropic/claude-3.5-sonnet", "context": "background"},
        "scenario": "opening situation",
        "num_turns": 2,
        "openrouter_api_key": "fake-key",
    }


def test_run_endpoint_returns_turns(monkeypatch):
    real_completion = litellm.completion

    def completion_with_mock(*args, **kwargs):
        kwargs["mock_response"] = "mocked reply"
        return real_completion(*args, **kwargs)

    monkeypatch.setattr(litellm, "completion", completion_with_mock)

    response = client.post("/api/run", json=make_valid_payload())

    assert response.status_code == 200
    turns = response.json()
    assert len(turns) == 2
    assert turns[0]["actions"]["A"] == "mocked reply"
    assert turns[0]["summary"] == "mocked reply"


def test_run_endpoint_rejects_invalid_config_with_400(monkeypatch):
    payload = make_valid_payload()
    payload["num_turns"] = 0  # fails GameConfig.validate()

    response = client.post("/api/run", json=payload)

    assert response.status_code == 400
    assert "num_turns" in response.json()["detail"]


def test_run_endpoint_rejects_malformed_body_with_422():
    payload = make_valid_payload()
    del payload["scenario"]  # missing required field entirely

    response = client.post("/api/run", json=payload)

    assert response.status_code == 422  # pydantic's shape validation, not ours


def test_index_page_is_served():
    response = client.get("/")
    assert response.status_code == 200
    assert "WargamingLLM" in response.text
    assert "Sentient Futures" in response.text
