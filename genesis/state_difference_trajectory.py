from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np

from .memory import MemoryRecord
from .state_innovation import combined_state


@dataclass(frozen=True)
class StateDifferenceTrajectoryEvaluationResult:
    samples: int
    zero_mae: float
    difference_mae: float
    shuffled_mae: float
    heldout_start_tick: int
    history_length: int

    @property
    def improvement(self) -> float:
        return self.zero_mae - self.difference_mae

    @property
    def beats_zero(self) -> bool:
        return self.difference_mae < self.zero_mae

    @property
    def beats_shuffled(self) -> bool:
        return self.difference_mae < self.shuffled_mae


class StateDifferenceTrajectoryPredictor:
    """Predict coherence innovation from consecutive non-coherence state differences."""

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

    def evaluate(
        self, records: Iterable[MemoryRecord]
    ) -> StateDifferenceTrajectoryEvaluationResult:
        ordered = sorted(records, key=lambda item: (item.identity, item.tick))
        if not ordered:
            return StateDifferenceTrajectoryEvaluationResult(
                0, 0.0, 0.0, 0.0, 0, self.history_length
            )

        min_tick = min(item.tick for item in ordered)
        max_tick = max(item.tick for item in ordered)
        heldout = min_tick + max(1, int((max_tick - min_tick) * self.train_fraction))

        groups: dict[int, list[MemoryRecord]] = {}
        for item in ordered:
            groups.setdefault(item.identity, []).append(item)

        train_x: list[tuple[float, ...]] = []
        train_y: list[float] = []
        test_x: list[tuple[float, ...]] = []
        test_y: list[float] = []

        for items in groups.values():
            items.sort(key=lambda item: item.tick)
            states = [combined_state(item) for item in items]
            differences = [
                tuple(b - a for a, b in zip(states[i - 1], states[i]))
                for i in range(1, len(states))
            ]
            for index in range(self.history_length, len(items)):
                window_records = items[index - self.history_length : index]
                target = items[index]
                ticks = [item.tick for item in window_records] + [target.tick]
                if self.require_consecutive and any(
                    ticks[j + 1] != ticks[j] + 1 for j in range(len(ticks) - 1)
                ):
                    continue

                row = tuple(
                    value
                    for difference in differences[
                        index - self.history_length : index
                    ]
                    for value in difference
                )
                delta = target.coherence - items[index - 1].coherence

                if target.tick < heldout:
                    train_x.append(row)
                    train_y.append(delta)
                else:
                    test_x.append(row)
                    test_y.append(delta)

        if not train_x or not test_x:
            return StateDifferenceTrajectoryEvaluationResult(
                0, 0.0, 0.0, 0.0, heldout, self.history_length
            )

        train = np.asarray(train_x, dtype=np.float64)
        test = np.asarray(test_x, dtype=np.float64)
        y = np.asarray(train_y, dtype=np.float64)

        mean = train.mean(axis=0)
        scale = train.std(axis=0)
        scale[scale == 0.0] = 1.0

        design = np.column_stack((np.ones(len(train)), (train - mean) / scale))
        regularizer = np.eye(design.shape[1])
        regularizer[0, 0] = 0.0
        coefficients = np.linalg.solve(
            design.T @ design + self.ridge * regularizer,
            design.T @ y,
        )

        prediction = np.column_stack(
            (np.ones(len(test)), (test - mean) / scale)
        ) @ coefficients

        shuffled = test.copy()
        np.random.default_rng(390001).shuffle(shuffled)
        shuffled_prediction = np.column_stack(
            (np.ones(len(shuffled)), (shuffled - mean) / scale)
        ) @ coefficients

        actual = np.asarray(test_y, dtype=np.float64)
        return StateDifferenceTrajectoryEvaluationResult(
            samples=len(actual),
            zero_mae=float(np.mean(np.abs(actual))),
            difference_mae=float(np.mean(np.abs(actual - prediction))),
            shuffled_mae=float(np.mean(np.abs(actual - shuffled_prediction))),
            heldout_start_tick=heldout,
            history_length=self.history_length,
        )
