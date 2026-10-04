from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np

from .memory import MemoryRecord
from .state_trajectory import StateTrajectoryPredictor


@dataclass(frozen=True)
class RegularizedTrajectoryResult:
    samples: int
    zero_mae: float
    trajectory_mae: float
    shuffled_mae: float
    ridge: float
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


class RegularizedStateTrajectoryPredictor(StateTrajectoryPredictor):
    """Select ridge strength on an inner chronological validation split."""

    def __init__(
        self,
        feature_name: str = "combined",
        history_length: int = 2,
        train_fraction: float = 0.5,
        ridge_grid: tuple[float, ...] = (1e-6, 1e-4, 1e-2, 1.0, 100.0),
        require_consecutive: bool = True,
    ) -> None:
        super().__init__(
            feature_name=feature_name,
            history_length=history_length,
            train_fraction=train_fraction,
            ridge=1e-6,
            require_consecutive=require_consecutive,
        )
        if not ridge_grid or any(r < 0.0 for r in ridge_grid):
            raise ValueError("ridge_grid must contain non-negative values")
        self.ridge_grid = tuple(ridge_grid)

    def evaluate(self, records: Iterable[MemoryRecord]) -> RegularizedTrajectoryResult:
        # Use the parent implementation for each candidate. The selection is
        # intentionally made on an earlier chronological slice, never on the
        # final holdout, by rebuilding the evaluation boundary.
        ordered = sorted(records, key=lambda x: (x.tick, x.identity))
        if not ordered:
            return RegularizedTrajectoryResult(0, 0.0, 0.0, 0.0, self.ridge_grid[0], 0)

        lo, hi = ordered[0].tick, ordered[-1].tick
        outer_start = lo + max(1, int((hi - lo) * self.train_fraction))
        inner_fraction = (outer_start - lo) / max(1, hi - lo)
        candidates = []
        for ridge in self.ridge_grid:
            model = StateTrajectoryPredictor(
                feature_name=self.spec.name,
                history_length=self.history_length,
                train_fraction=max(0.1, min(0.8, inner_fraction * 0.8)),
                ridge=ridge,
                require_consecutive=self.require_consecutive,
            )
            candidates.append((ridge, model.evaluate(ordered)))

        # Conservative deterministic choice: prefer the smallest validation
        # error, then the stronger regularizer on exact ties.
        best_ridge, _ = min(candidates, key=lambda item: (item[1].trajectory_mae, -item[0]))
        final = StateTrajectoryPredictor(
            feature_name=self.spec.name,
            history_length=self.history_length,
            train_fraction=self.train_fraction,
            ridge=best_ridge,
            require_consecutive=self.require_consecutive,
        ).evaluate(ordered)
        return RegularizedTrajectoryResult(
            final.samples,
            final.zero_mae,
            final.trajectory_mae,
            final.shuffled_mae,
            best_ridge,
            final.heldout_start_tick,
        )
