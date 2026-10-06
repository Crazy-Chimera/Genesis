from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np

from .memory import MemoryRecord
from .state_innovation import combined_state


@dataclass(frozen=True)
class StateDynamicsEvaluationResult:
    samples: int
    zero_mae: float
    dynamics_mae: float
    shuffled_mae: float
    heldout_start_tick: int
    history_length: int

    @property
    def improvement(self) -> float:
        return self.zero_mae - self.dynamics_mae

    @property
    def beats_zero(self) -> bool:
        return self.dynamics_mae < self.zero_mae

    @property
    def beats_shuffled(self) -> bool:
        return self.dynamics_mae < self.shuffled_mae


def dynamics_state(record: MemoryRecord) -> tuple[float, ...]:
    x = np.asarray(combined_state(record), dtype=np.float64)
    return (
        float(np.mean(x)),
        float(np.std(x)),
        float(np.mean(np.abs(x))),
        float(np.sqrt(np.mean(x * x))),
        float(np.max(x)),
        float(np.min(x)),
    )


class StateDynamicsPredictor:
    """Predict coherence innovation from short trajectories of compressed state motion."""

    def __init__(
        self,
        history_length: int = 3,
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

    def evaluate(self, records: Iterable[MemoryRecord]) -> StateDynamicsEvaluationResult:
        ordered = sorted(records, key=lambda item: (item.tick, item.identity))
        if not ordered:
            return StateDynamicsEvaluationResult(0, 0.0, 0.0, 0.0, 0, self.history_length)

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
            dynamics = [dynamics_state(item) for item in items]
            for i in range(self.history_length, len(items)):
                window = items[i - self.history_length:i]
                target = items[i]
                ticks = [item.tick for item in window] + [target.tick]
                if self.require_consecutive and any(
                    ticks[j + 1] != ticks[j] + 1 for j in range(len(ticks) - 1)
                ):
                    continue

                deltas = [
                    tuple(dynamics[i - self.history_length + j + 1][k] - dynamics[i - self.history_length + j][k]
                          for k in range(6))
                    for j in range(self.history_length - 1)
                ]
                row = tuple(value for delta in deltas for value in delta)
                delta_c = target.coherence - window[-1].coherence

                if target.tick < heldout:
                    train_x.append(row)
                    train_y.append(delta_c)
                else:
                    test_x.append(row)
                    test_y.append(delta_c)

        if not train_x or not test_x:
            return StateDynamicsEvaluationResult(0, 0.0, 0.0, 0.0, heldout, self.history_length)

        train = np.asarray(train_x, dtype=np.float64)
        test = np.asarray(test_x, dtype=np.float64)
        y = np.asarray(train_y, dtype=np.float64)

        mean = train.mean(axis=0)
        scale = train.std(axis=0)
        scale[scale == 0.0] = 1.0

        x = np.column_stack((np.ones(len(train)), (train - mean) / scale))
        v = np.column_stack((np.ones(len(test)), (test - mean) / scale))
        reg = np.eye(x.shape[1])
        reg[0, 0] = 0.0
        coef = np.linalg.solve(x.T @ x + self.ridge * reg, x.T @ y)

        pred = v @ coef
        shuffled = test.copy()
        np.random.default_rng(390001).shuffle(shuffled)
        shuffled_pred = np.column_stack(
            (np.ones(len(shuffled)), (shuffled - mean) / scale)
        ) @ coef

        actual = np.asarray(test_y, dtype=np.float64)
        return StateDynamicsEvaluationResult(
            samples=len(actual),
            zero_mae=float(np.mean(np.abs(actual))),
            dynamics_mae=float(np.mean(np.abs(actual - pred))),
            shuffled_mae=float(np.mean(np.abs(actual - shuffled_pred))),
            heldout_start_tick=heldout,
            history_length=self.history_length,
        )
