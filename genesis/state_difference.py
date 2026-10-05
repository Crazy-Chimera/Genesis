from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np

from .memory import MemoryRecord
from .state_innovation import STATE_FEATURES_WITH_COMBINED, StateFeatureSpec


@dataclass(frozen=True)
class StateDifferenceEvaluationResult:
    samples: int
    zero_mae: float
    difference_mae: float
    shuffled_mae: float
    heldout_start_tick: int
    feature_name: str
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


class StateDifferencePredictor:
    """Predict coherence innovation from a trajectory of state differences."""

    def __init__(
        self,
        feature_name: str = "combined",
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

        matches = [
            spec for spec in STATE_FEATURES_WITH_COMBINED
            if spec.name == feature_name
        ]
        if not matches:
            raise ValueError(f"unknown state feature: {feature_name}")

        self.spec: StateFeatureSpec = matches[0]
        self.history_length = history_length
        self.train_fraction = train_fraction
        self.ridge = ridge
        self.require_consecutive = require_consecutive

    def evaluate(
        self, records: Iterable[MemoryRecord]
    ) -> StateDifferenceEvaluationResult:
        ordered = sorted(records, key=lambda item: (item.tick, item.identity))
        if not ordered:
            return StateDifferenceEvaluationResult(
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
            items.sort(key=lambda item: item.tick)
            vectors = []
            valid_items = []
            for item in items:
                vector = tuple(float(v) for v in self.spec.feature(item))
                if len(vector) != self.spec.width:
                    continue
                vectors.append(vector)
                valid_items.append(item)

            for i in range(self.history_length + 1, len(valid_items)):
                state_window = vectors[i - self.history_length - 1 : i + 1]
                tick_window = [
                    item.tick
                    for item in valid_items[i - self.history_length - 1 : i + 1]
                ]

                if self.require_consecutive and any(
                    b != a + 1
                    for a, b in zip(tick_window, tick_window[1:])
                ):
                    continue

                differences = [
                    tuple(
                        state_window[j][k] - state_window[j - 1][k]
                        for k in range(self.spec.width)
                    )
                    for j in range(1, len(state_window))
                ]
                row = tuple(v for difference in differences for v in difference)
                delta = (
                    valid_items[i].coherence
                    - valid_items[i - 1].coherence
                )

                if valid_items[i].tick < heldout:
                    train_x.append(row)
                    train_y.append(delta)
                else:
                    test_x.append(row)
                    test_y.append(delta)

        if not train_x or not test_x:
            return StateDifferenceEvaluationResult(
                0, 0.0, 0.0, 0.0, heldout, self.spec.name, self.history_length
            )

        train = np.asarray(train_x, dtype=np.float64)
        test = np.asarray(test_x, dtype=np.float64)
        target = np.asarray(train_y, dtype=np.float64)

        mean = train.mean(axis=0)
        scale = train.std(axis=0)
        scale[scale == 0.0] = 1.0

        design = np.column_stack((np.ones(len(train)), (train - mean) / scale))
        regularizer = np.eye(design.shape[1])
        regularizer[0, 0] = 0.0

        coefficients = np.linalg.solve(
            design.T @ design + self.ridge * regularizer,
            design.T @ target,
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
        return StateDifferenceEvaluationResult(
            samples=len(actual),
            zero_mae=float(np.mean(np.abs(actual))),
            difference_mae=float(np.mean(np.abs(actual - prediction))),
            shuffled_mae=float(np.mean(np.abs(actual - shuffled_prediction))),
            heldout_start_tick=heldout,
            feature_name=self.spec.name,
            history_length=self.history_length,
        )
