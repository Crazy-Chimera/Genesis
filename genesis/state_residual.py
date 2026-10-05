from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np

from .memory import MemoryRecord
from .state_innovation import STATE_FEATURES_WITH_COMBINED, StateFeatureSpec


@dataclass(frozen=True)
class StateResidualTrajectoryEvaluationResult:
    samples: int
    zero_mae: float
    residual_mae: float
    shuffled_mae: float
    heldout_start_tick: int
    feature_name: str
    history_length: int

    @property
    def improvement(self) -> float:
        return self.zero_mae - self.residual_mae

    @property
    def beats_zero(self) -> bool:
        return self.residual_mae < self.zero_mae

    @property
    def beats_shuffled(self) -> bool:
        return self.residual_mae < self.shuffled_mae


class StateResidualTrajectoryPredictor:
    """Predict next coherence innovation from movement of non-coherence state."""

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

    def evaluate(
        self, records: Iterable[MemoryRecord]
    ) -> StateResidualTrajectoryEvaluationResult:
        ordered = sorted(records, key=lambda x: (x.identity, x.tick))
        if not ordered:
            return StateResidualTrajectoryEvaluationResult(
                0, 0.0, 0.0, 0.0, 0, self.spec.name, self.history_length
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
            items.sort(key=lambda x: x.tick)
            states = [
                np.asarray(self.spec.feature(item), dtype=np.float64)
                for item in items
            ]
            for i in range(1, len(items)):
                if self.require_consecutive and items[i].tick != items[i - 1].tick + 1:
                    continue
                if len(states[i]) != self.spec.width:
                    continue

                residuals = [
                    states[j] - states[j - 1]
                    for j in range(max(1, i - self.history_length), i + 1)
                ]
                if len(residuals) < self.history_length:
                    continue

                window_items = items[i - self.history_length:i]
                ticks = [item.tick for item in window_items] + [items[i].tick]
                if self.require_consecutive and any(
                    ticks[j + 1] != ticks[j] + 1 for j in range(len(ticks) - 1)
                ):
                    continue

                row = tuple(
                    float(value)
                    for residual in residuals[:-1]
                    for value in residual
                )
                delta = items[i].coherence - items[i - 1].coherence
                if items[i].tick < heldout:
                    train_x.append(row)
                    train_y.append(delta)
                else:
                    test_x.append(row)
                    test_y.append(delta)

        if not train_x or not test_x:
            return StateResidualTrajectoryEvaluationResult(
                0, 0.0, 0.0, 0.0, heldout, self.spec.name, self.history_length
            )

        train = np.asarray(train_x, dtype=np.float64)
        test = np.asarray(test_x, dtype=np.float64)
        y = np.asarray(train_y, dtype=np.float64)
        mean = train.mean(axis=0)
        scale = train.std(axis=0)
        scale[scale == 0.0] = 1.0

        x = np.column_stack((np.ones(len(train)), (train - mean) / scale))
        v = np.column_stack((np.ones(len(test)), (test - mean) / scale))
        regularizer = np.eye(x.shape[1])
        regularizer[0, 0] = 0.0
        coefficients = np.linalg.solve(
            x.T @ x + self.ridge * regularizer, x.T @ y
        )

        prediction = v @ coefficients
        shuffled = test.copy()
        np.random.default_rng(390001).shuffle(shuffled)
        shuffled_prediction = np.column_stack(
            (np.ones(len(shuffled)), (shuffled - mean) / scale)
        ) @ coefficients

        actual = np.asarray(test_y, dtype=np.float64)
        return StateResidualTrajectoryEvaluationResult(
            len(actual),
            float(np.mean(np.abs(actual))),
            float(np.mean(np.abs(actual - prediction))),
            float(np.mean(np.abs(actual - shuffled_prediction))),
            heldout,
            self.spec.name,
            self.history_length,
        )
