from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np

from .memory import MemoryRecord
from .population_innovation import population_state


@dataclass(frozen=True)
class PopulationTrajectoryEvaluationResult:
    samples: int
    zero_mae: float
    trajectory_mae: float
    shuffled_mae: float
    heldout_start_tick: int
    history_length: int

    @property
    def improvement(self) -> float:
        return self.zero_mae - self.trajectory_mae

    @property
    def beats_zero(self) -> bool:
        return self.trajectory_mae < self.zero_mae

    @property
    def beats_shuffled(self) -> bool:
        return self.trajectory_mae < self.shuffled_mae


class PopulationTrajectoryPredictor:
    """Predict next population-mean coherence innovation from population-state history."""

    def __init__(
        self,
        history_length: int = 2,
        train_fraction: float = 0.5,
        ridge: float = 1e-6,
        require_consecutive: bool = True,
    ) -> None:
        if history_length < 2:
            raise ValueError("history_length must be >= 2")
        if not 0.0 < train_fraction < 1.0:
            raise ValueError("train_fraction must be between 0 and 1")
        if ridge < 0.0:
            raise ValueError("ridge must be >= 0")
        self.history_length = history_length
        self.train_fraction = train_fraction
        self.ridge = ridge
        self.require_consecutive = require_consecutive

    def evaluate(self, records: Iterable[MemoryRecord]) -> PopulationTrajectoryEvaluationResult:
        by_tick: dict[int, list[MemoryRecord]] = {}
        for record in records:
            by_tick.setdefault(record.tick, []).append(record)
        ticks = sorted(by_tick)
        if len(ticks) <= self.history_length:
            return PopulationTrajectoryEvaluationResult(
                0, 0.0, 0.0, 0.0, 0, self.history_length
            )

        states = {tick: population_state(by_tick[tick])[1] for tick in ticks}
        coherence = {
            tick: float(np.mean([r.coherence for r in by_tick[tick]]))
            for tick in ticks
        }
        heldout = ticks[0] + max(1, int((ticks[-1] - ticks[0]) * self.train_fraction))

        train_x: list[tuple[float, ...]] = []
        train_y: list[float] = []
        test_x: list[tuple[float, ...]] = []
        test_y: list[float] = []

        for i in range(self.history_length, len(ticks)):
            window_ticks = ticks[i - self.history_length:i]
            target_tick = ticks[i]
            check_ticks = window_ticks + [target_tick]
            if self.require_consecutive and any(
                check_ticks[j + 1] != check_ticks[j] + 1
                for j in range(len(check_ticks) - 1)
            ):
                continue
            row = tuple(value for tick in window_ticks for value in states[tick])
            delta = coherence[target_tick] - coherence[window_ticks[-1]]
            if target_tick < heldout:
                train_x.append(row)
                train_y.append(delta)
            else:
                test_x.append(row)
                test_y.append(delta)

        if not train_x or not test_x:
            return PopulationTrajectoryEvaluationResult(
                0, 0.0, 0.0, 0.0, heldout, self.history_length
            )

        train = np.asarray(train_x, dtype=float)
        test = np.asarray(test_x, dtype=float)
        y = np.asarray(train_y, dtype=float)
        mean = train.mean(axis=0)
        scale = train.std(axis=0)
        scale[scale == 0.0] = 1.0

        design = np.column_stack((np.ones(len(train)), (train - mean) / scale))
        reg = np.eye(design.shape[1])
        reg[0, 0] = 0.0
        coef = np.linalg.solve(
            design.T @ design + self.ridge * reg,
            design.T @ y,
        )
        pred = np.column_stack((np.ones(len(test)), (test - mean) / scale)) @ coef

        shuffled = test.copy()
        np.random.default_rng(390001).shuffle(shuffled)
        shuffled_pred = np.column_stack(
            (np.ones(len(shuffled)), (shuffled - mean) / scale)
        ) @ coef

        actual = np.asarray(test_y, dtype=float)
        return PopulationTrajectoryEvaluationResult(
            len(actual),
            float(np.mean(np.abs(actual))),
            float(np.mean(np.abs(actual - pred))),
            float(np.mean(np.abs(actual - shuffled_pred))),
            heldout,
            self.history_length,
        )
