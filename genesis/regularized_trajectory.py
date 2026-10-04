from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .memory import MemoryRecord
from .state_trajectory import StateTrajectoryPredictor


@dataclass(frozen=True)
class RidgeSweepResult:
    ridge: float
    samples: int
    zero_mae: float
    trajectory_mae: float
    shuffled_mae: float
    heldout_start_tick: int

    @property
    def improvement(self) -> float:
        return self.zero_mae - self.trajectory_mae

    @property
    def beats_zero(self) -> bool:
        return self.trajectory_mae < self.zero_mae

    @property
    def beats_shuffled(self) -> bool:
        return self.trajectory_mae < self.shuffled_mae


def evaluate_ridge_sweep(
    records: Iterable[MemoryRecord],
    *,
    history_length: int = 2,
    ridge_grid: tuple[float, ...] = (1e-6, 1e-4, 1e-2, 1.0, 100.0),
    train_fraction: float = 0.5,
) -> tuple[RidgeSweepResult, ...]:
    """Report a fixed chronological holdout for each ridge; no test selection."""
    if not ridge_grid or any(r < 0.0 for r in ridge_grid):
        raise ValueError("ridge_grid must contain non-negative values")

    ordered = tuple(records)
    results = []
    for ridge in ridge_grid:
        result = StateTrajectoryPredictor(
            feature_name="combined",
            history_length=history_length,
            train_fraction=train_fraction,
            ridge=ridge,
            require_consecutive=True,
        ).evaluate(ordered)
        results.append(
            RidgeSweepResult(
                ridge,
                result.samples,
                result.zero_mae,
                result.trajectory_mae,
                result.shuffled_mae,
                result.heldout_start_tick,
            )
        )
    return tuple(results)
