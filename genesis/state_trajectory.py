from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np

from .memory import MemoryRecord
from .state_innovation import STATE_FEATURES_WITH_COMBINED, StateFeatureSpec


@dataclass(frozen=True)
class StateTrajectoryEvaluationResult:
    samples: int
    zero_mae: float
    trajectory_mae: float
    shuffled_mae: float
    heldout_start_tick: int
    feature_name: str
    history_length: int
    differences: bool = False

    @property
    def improvement(self) -> float:
        return self.zero_mae - self.trajectory_mae

    @property
    def beats_zero(self) -> bool:
        return self.trajectory_mae < self.zero_mae

    @property
    def beats_shuffled(self) -> bool:
        return self.trajectory_mae < self.shuffled_mae


class StateTrajectoryPredictor:
    """Predict next coherence innovation from a short non-coherence state trajectory."""

    def __init__(
        self,
        feature_name="combined",
        history_length=3,
        train_fraction=0.5,
        ridge=1e-6,
        require_consecutive=True,
        differences=False,
    ):
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
        self.differences = differences

    def evaluate(self, records: Iterable[MemoryRecord]):
        ordered = sorted(records, key=lambda x: (x.tick, x.identity))
        if not ordered:
            return StateTrajectoryEvaluationResult(
                0, 0, 0, 0, 0, self.spec.name, self.history_length, self.differences
            )

        lo, hi = ordered[0].tick, ordered[-1].tick
        heldout = lo + max(1, int((hi - lo) * self.train_fraction))
        groups = {}
        for item in ordered:
            groups.setdefault(item.identity, []).append(item)

        tx, ty, vx, vy = [], [], [], []
        for items in groups.values():
            items.sort(key=lambda x: x.tick)
            start = self.history_length + 1 if self.differences else self.history_length
            for i in range(start, len(items)):
                window = items[i - self.history_length:i]
                target = items[i]
                source_window = (
                    items[i - self.history_length - 1:i]
                    if self.differences else window
                )
                ticks = [x.tick for x in source_window] + [target.tick]
                if self.require_consecutive and any(
                    ticks[j + 1] != ticks[j] + 1 for j in range(len(ticks) - 1)
                ):
                    continue

                vectors = [
                    np.asarray(tuple(float(v) for v in self.spec.feature(x)), dtype=float)
                    for x in source_window
                ]
                if any(len(v) != self.spec.width for v in vectors):
                    continue

                if self.differences:
                    vectors = [vectors[j + 1] - vectors[j] for j in range(self.history_length)]

                row = tuple(float(v) for vector in vectors for v in vector)
                delta = target.coherence - window[-1].coherence

                if target.tick < heldout:
                    tx.append(row)
                    ty.append(delta)
                else:
                    vx.append(row)
                    vy.append(delta)

        if not tx or not vx:
            return StateTrajectoryEvaluationResult(
                0, 0, 0, 0, heldout, self.spec.name, self.history_length, self.differences
            )

        train = np.asarray(tx, float)
        test = np.asarray(vx, float)
        y = np.asarray(ty, float)
        mean = train.mean(0)
        scale = train.std(0)
        scale[scale == 0] = 1
        X = np.column_stack((np.ones(len(train)), (train - mean) / scale))
        V = np.column_stack((np.ones(len(test)), (test - mean) / scale))
        reg = np.eye(X.shape[1])
        reg[0, 0] = 0
        coef = np.linalg.solve(X.T @ X + self.ridge * reg, X.T @ y)
        pred = V @ coef

        shuffled = test.copy()
        np.random.default_rng(390001).shuffle(shuffled)
        sp = np.column_stack((np.ones(len(shuffled)), (shuffled - mean) / scale)) @ coef
        actual = np.asarray(vy, float)

        return StateTrajectoryEvaluationResult(
            len(actual),
            float(np.mean(np.abs(actual))),
            float(np.mean(np.abs(actual - pred))),
            float(np.mean(np.abs(actual - sp))),
            heldout,
            self.spec.name,
            self.history_length,
            self.differences,
        )
