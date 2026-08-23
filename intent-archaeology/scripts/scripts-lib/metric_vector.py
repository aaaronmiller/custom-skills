"""Metric vector definitions. See references/metric_vector.md.

The status vector has six components that sum to 1.0 per project:
  completed, in_progress, drifted, superseded, abandoned, not_begun

Never report a single completion percentage. See anti-metrics in
references/metric_vector.md.
"""
from __future__ import annotations

from dataclasses import dataclass, field

COMPONENTS = ["completed", "in_progress", "drifted", "superseded", "abandoned", "not_begun"]


@dataclass
class StatusVector:
    project_id: int
    tranche_id: int
    completed: float = 0.0
    in_progress: float = 0.0
    drifted: float = 0.0
    superseded: float = 0.0
    abandoned: float = 0.0
    not_begun: float = 0.0

    def total(self) -> float:
        return sum(getattr(self, c) for c in COMPONENTS)

    def normalize(self) -> "StatusVector":
        """Normalize so components sum to 1.0. Returns new vector."""
        t = self.total()
        if t == 0:
            return StatusVector(self.project_id, self.tranche_id)
        return StatusVector(
            project_id=self.project_id,
            tranche_id=self.tranche_id,
            **{c: getattr(self, c) / t for c in COMPONENTS},
        )

    def to_dict(self) -> dict:
        return {c: getattr(self, c) for c in COMPONENTS}

    def summary_line(self) -> str:
        """One-line human summary for reports."""
        return " | ".join(f"{c}={getattr(self, c):.2f}" for c in COMPONENTS if getattr(self, c) > 0)


# Anti-metrics: explicitly forbidden in reports.
# See references/failure_modes.md #4 (reward hacking).
ANTI_METRICS = [
    "single_completion_percentage",
    "lines_of_code_per_intent",
    "time_spent_per_intent",
    "agent_turn_count_per_intent",
]


def assert_no_anti_metric(report: dict) -> None:
    """Fail loud if an anti-metric appears in a report dict."""
    for am in ANTI_METRICS:
        if am in report:
            raise AssertionError(
                f"Anti-metric {am!r} forbidden in status vector reports. "
                f"See references/metric_vector.md."
            )
