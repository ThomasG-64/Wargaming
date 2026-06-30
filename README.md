# AI-Assisted Wargaming for Animal Welfare

An LLM-powered multi-stakeholder policy wargame that simulates how AI's
growing role in decision-making (corporate, regulatory, individual)
shapes animal welfare outcomes. Stakeholder agents (industry, regulators,
NGOs, ...) respond turn-by-turn to escalating scenarios; a referee agent
adjudicates outcomes each turn.

See [docs/research-plan.docx](docs/research-plan.docx) for the full
research background and rationale.

## Status

Week 1 prototype: 3 agents, 1 scenario ("The Optimizer"), 5-turn
automated simulation. See [the roadmap](#roadmap) below.

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
4. Copy `.env.example` to `.env` and fill in at least one API key
   (e.g. `ANTHROPIC_API_KEY`). Different agents can use different
   providers/models — see `src/wargame/agents.py`.

## Running the prototype

```
venv\Scripts\python.exe scripts/run_prototype.py
```

Writes a Markdown transcript to `output/` (gitignored).

## Project layout

```
src/wargame/    importable package: agents, scenarios, the turn engine, the LLM wrapper
scripts/        entry-point scripts that use the package
tests/          automated tests (no API key required)
docs/           design docs
output/         generated transcripts (gitignored)
```

## Roadmap

- **Week 1** — foundation: 3 agents, 1 scenario, 5-turn loop, multi-model support. *(current)*
- **Week 2** — more scenarios + agents, welfare-scoring module.
- **Week 3** — hybrid human/AI mode, structured JSON output, agent memory across turns.
- **Week 4** — polish, sample transcripts, open-sourcing readiness.
