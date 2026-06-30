"""Scenario definitions. A scenario is just the opening situation —
everything that happens after turn 1 emerges from what the agents do."""

from dataclasses import dataclass


@dataclass
class Scenario:
    name: str
    opening_situation: str


THE_OPTIMIZER = Scenario(
    name="The Optimizer",
    opening_situation=(
        "A major poultry integrator has deployed an AI system that "
        "autonomously adjusts stocking density, lighting schedules, and "
        "feed formulation in real time to minimize cost-per-pound across "
        "its broiler chicken operations. The system has been live for "
        "three months. Early production data shows a 4% reduction in "
        "cost-per-pound. The regulator has no existing framework to "
        "evaluate AI-driven changes to farm operating parameters. "
        "An animal welfare NGO has just published a report raising "
        "questions about what the AI's optimization actually optimized "
        "for, and whether anyone outside the company can verify it."
    ),
)
