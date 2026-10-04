from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable
import numpy as np

from .memory import MemoryRecord
from .state_innovation import STATE_FEATURES_WITH_COMBINED, StateFeatureSpec


@dataclass(frozen=True)
class StateMotionEvaluationResult:
    samples: int
    zero_mae: float
    motion_mae: float
    shuffled_mae: float
    heldout_start_tick: int
    feature_name: str
    history_length: int

    @property
    def improvement(self) -> float:
        return self.zero_mae - self.motion_mae

    @property
    def beats_zero(self) -> bool:
        return self.motion_mae < self.zero_mae

    @property
    def beats_shuffled(self) -> bool:
        return self.motion_mae < self.shuffled_mae


class StateMotionPredictor:
    """Predict next coherence innovation from first differences of non-coherence state."""

    def __init__(
        self,
        feature_name: str = "combined",
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
        matches = [s for s in STATE_FEATURES_WITH_COMBINED if s.name == feature_name]
        if not matches:
            raise ValueError(f"unknown state feature: {feature_name}")
        self.spec: StateFeatureSpec = matches[0]
        self.history_length = history_length
        self.train_fraction = train_fraction
        self.ridge = ridge
        self.require_consecutive = require_consecutive

    def evaluate(self, records: Iterable[MemoryRecord]) -> StateMotionEvaluationResult:
        ordered = sorted(records, key=lambda x: (x.tick, x.identity))
        if not ordered:
            return StateMotionEvaluationResult(
                0, 0.0, 0.0, 0.0, 0, self.spec.name, self.history_length
            )

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
            for i in range(self.history_length, len(items)):
                window = items[i - self.history_length : i]
                target = items[i]
                ticks = [x.tick for x in window] + [target.tick]
                if self.require_consecutive and any(
                    ticks[j + 1] != ticks[j] + 1 for j in range(len(ticks) - 1)
                ):
                    continue

                vectors = [
                    np.asarray(self.spec.feature(x), dtype=np.float64)
                    for x in window
                ]
                if any(v.size != self.spec.width for v in vectors):
                    continue

                deltas = [vectors[j + 1] - vectors[j] for j in range(len(vectors) - 1)]
                row = tuple(float(v) for delta in deltas for v in delta)
                delta_target = target.coherence - window[-1].coherence

                if target.tick < heldout:
                    train_x.append(row)
                    train_y.append(delta_target)
                else:
                    test_x.append(row)
                    test_y.append(delta_target)

        if not train_x or not test_x:
            return StateMotionEvaluationResult(
                0, 0.0, 0.0, 0.0, heldout, self.spec.name, self.history_length
            )

        train = np.asarray(train_x, dtype=np.float64)
        test = np.asarray(test_x, dtype=np.float64)
        y = np.asarray(train_y, dtype=np.float64)

        mean = train.mean(axis=0)
        scale = train.std(axis=0)
        scale[scale == 0.0] = 1.0

        X = np.column_stack((np.ones(len(train)), (train - mean) / scale))
        V = np.column_stack((np.ones(len(test)), (test - mean) / scale))
        reg = np.eye(X.shape[1])
        reg[0, 0] = 0.0
        coef = np.linalg.solve(X.T @ X + self.ridge * reg, X.T @ y)

        prediction = V @ coef
        shuffled = test.copy()
        np.random.default_rng(390001).shuffle(shuffled)
        shuffled_prediction = np.column_stack(
            (np.ones(len(shuffled)), (shuffled - mean) / scale)
        ) @ coef

        actual = np.asarray(test_y, dtype=np.float64)
        return StateMotionEvaluationResult(
            len(actual),
            float(np.mean(np.abs(actual))),
            float(np.mean(np.abs(actual - prediction))),
            float(np.mean(np.abs(actual - shuffled_prediction))),
            heldout,
            self.spec.name,
            self.history_length,
        )
