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
    history_length: int

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
    """Predict next coherence innovation from first differences of non-coherence state."""

    def __init__(
        self,
        history_length: int = 2,
        train_fraction: float = 0.5,
        ridge: float = 1e-6,
        require_consecutive: bool = True,
    ) -> None:
        if history_length < 1:
            raise ValueError("history_length must be >= 1")
        if not 0.0 < train_fraction < 1.0:
            raise ValueError("train_fraction must be between 0 and 1")
        if ridge < 0.0:
            raise ValueError("ridge must be >= 0")
        self.history_length = history_length
        self.train_fraction = train_fraction
        self.ridge = ridge
        self.require_consecutive = require_consecutive

    def evaluate(self, records: Iterable[MemoryRecord]) -> StateVelocityEvaluationResult:
        ordered = sorted(records, key=lambda x: (x.tick, x.identity))
        if not ordered:
            return StateVelocityEvaluationResult(0, 0.0, 0.0, 0.0, 0, self.history_length)

        lo, hi = ordered[0].tick, ordered[-1].tick
        heldout = lo + max(1, int((hi - lo) * self.train_fraction))
        groups: dict[int, list[MemoryRecord]] = {}
        for item in ordered:
            groups.setdefault(item.identity, []).append(item)

        train_x: list[tuple[float, ...]] = []
        train_y: list[float] = []
        test_x: list[tuple[float, ...]] = []
        test_y: list[float] = []

        for items in groups.values():
            items.sort(key=lambda x: x.tick)
            states = [combined_state(item) for item in items]
            for i in range(self.history_length + 1, len(items)):
                relevant = items[i - self.history_length - 1 : i]
                ticks = [x.tick for x in relevant] + [items[i].tick]
                if self.require_consecutive and any(
                    ticks[j + 1] != ticks[j] + 1 for j in range(len(ticks) - 1)
                ):
                    continue
                velocities = [
                    np.asarray(states[j + 1], dtype=float) - np.asarray(states[j], dtype=float)
                    for j in range(i - self.history_length, i)
                ]
                row = tuple(float(v) for velocity in velocities for v in velocity)
                delta = items[i].coherence - items[i - 1].coherence
                if items[i].tick < heldout:
                    train_x.append(row)
                    train_y.append(delta)
                else:
                    test_x.append(row)
                    test_y.append(delta)

        if not train_x or not test_x:
            return StateVelocityEvaluationResult(
                0, 0.0, 0.0, 0.0, heldout, self.history_length
            )

        train = np.asarray(train_x, dtype=float)
        test = np.asarray(test_x, dtype=float)
        y = np.asarray(train_y, dtype=float)
        mean = train.mean(axis=0)
        scale = train.std(axis=0)
        scale[scale == 0] = 1
        X = np.column_stack((np.ones(len(train)), (train - mean) / scale))
        V = np.column_stack((np.ones(len(test)), (test - mean) / scale))
        reg = np.eye(X.shape[1])
        reg[0, 0] = 0
        coef = np.linalg.solve(X.T @ X + self.ridge * reg, X.T @ y)
        pred = V @ coef

        shuffled = test.copy()
        np.random.default_rng(390001).shuffle(shuffled)
        shuffled_pred = np.column_stack(
            (np.ones(len(shuffled)), (shuffled - mean) / scale)
        ) @ coef

        actual = np.asarray(test_y, dtype=float)
        return StateVelocityEvaluationResult(
            len(actual),
            float(np.mean(np.abs(actual))),
            float(np.mean(np.abs(actual - pred))),
            float(np.mean(np.abs(actual - shuffled_pred))),
            heldout,
            self.history_length,
        )
