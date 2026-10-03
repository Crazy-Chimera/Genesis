from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np

from .memory import MemoryRecord
from .state_innovation import combined_state


@dataclass(frozen=True)
class StateVelocityEvaluationResult:
    samples: int
    zero_mae: float
    velocity_mae: float
    shuffled_mae: float
    heldout_start_tick: int

    @property
    def improvement(self) -> float:
        return self.zero_mae - self.velocity_mae

    @property
    def beats_zero(self) -> bool:
        return self.velocity_mae < self.zero_mae

    @property
    def beats_shuffled(self) -> bool:
        return self.velocity_mae < self.shuffled_mae


class StateVelocityPredictor:
    """Predict next coherence innovation from non-coherence state velocity."""

    def __init__(self, train_fraction: float = 0.5, ridge: float = 1e-6) -> None:
        if not 0.0 < train_fraction < 1.0:
            raise ValueError("train_fraction must be between 0 and 1")
        if ridge < 0.0:
            raise ValueError("ridge must be >= 0")
        self.train_fraction = train_fraction
        self.ridge = ridge

    def evaluate(self, records: Iterable[MemoryRecord]) -> StateVelocityEvaluationResult:
        ordered = sorted(records, key=lambda item: (item.tick, item.identity))
        if not ordered:
            return StateVelocityEvaluationResult(0, 0.0, 0.0, 0.0, 0)

        min_tick, max_tick = ordered[0].tick, ordered[-1].tick
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
            for i in range(1, len(items)):
                previous, current = items[i - 1], items[i]
                if current.tick != previous.tick + 1:
                    continue
                previous_state = np.asarray(combined_state(previous), dtype=float)
                current_state = np.asarray(combined_state(current), dtype=float)
                row = tuple(current_state - previous_state)
                delta = current.coherence - previous.coherence
                if current.tick < heldout:
                    train_x.append(row)
                    train_y.append(delta)
                else:
                    test_x.append(row)
                    test_y.append(delta)

        if not train_x or not test_x:
            return StateVelocityEvaluationResult(0, 0.0, 0.0, 0.0, heldout)

        train = np.asarray(train_x)
        test = np.asarray(test_x)
        target = np.asarray(train_y)

        mean = train.mean(0)
        scale = train.std(0)
        scale[scale == 0.0] = 1.0

        x = np.column_stack((np.ones(len(train)), (train - mean) / scale))
        v = np.column_stack((np.ones(len(test)), (test - mean) / scale))
        regularizer = np.eye(x.shape[1])
        regularizer[0, 0] = 0.0
        coefficients = np.linalg.solve(
            x.T @ x + self.ridge * regularizer,
            x.T @ target,
        )

        prediction = v @ coefficients
        shuffled = test.copy()
        np.random.default_rng(390001).shuffle(shuffled)
        shuffled_prediction = np.column_stack(
            (np.ones(len(shuffled)), (shuffled - mean) / scale)
        ) @ coefficients

        actual = np.asarray(test_y)
        return StateVelocityEvaluationResult(
            len(actual),
            float(np.mean(np.abs(actual))),
            float(np.mean(np.abs(actual - prediction))),
            float(np.mean(np.abs(actual - shuffled_prediction))),
            heldout,
        )
