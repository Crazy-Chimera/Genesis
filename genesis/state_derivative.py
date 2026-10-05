from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np

from .memory import MemoryRecord
from .state_innovation import STATE_FEATURES_WITH_COMBINED


@dataclass(frozen=True)
class StateDerivativeEvaluationResult:
    samples: int
    zero_mae: float
    derivative_mae: float
    shuffled_mae: float
    heldout_start_tick: int
    feature_name: str

    @property
    def improvement(self) -> float:
        return self.zero_mae - self.derivative_mae

    @property
    def beats_zero(self) -> bool:
        return self.derivative_mae < self.zero_mae

    @property
    def beats_shuffled(self) -> bool:
        return self.derivative_mae < self.shuffled_mae


class StateDerivativePredictor:
    """Predict next coherence innovation from a non-coherence state change."""

    def __init__(
        self,
        feature_name: str = "combined",
        train_fraction: float = 0.5,
        ridge: float = 1e-6,
        require_consecutive: bool = True,
    ) -> None:
        if not 0.0 < train_fraction < 1.0:
            raise ValueError("train_fraction must be between 0 and 1")
        if ridge < 0.0:
            raise ValueError("ridge must be >= 0")
        matches = [s for s in STATE_FEATURES_WITH_COMBINED if s.name == feature_name]
        if not matches:
            raise ValueError(f"unknown state feature: {feature_name}")
        self.spec = matches[0]
        self.train_fraction = train_fraction
        self.ridge = ridge
        self.require_consecutive = require_consecutive

    def evaluate(self, records: Iterable[MemoryRecord]) -> StateDerivativeEvaluationResult:
        ordered = sorted(records, key=lambda item: (item.tick, item.identity))
        if not ordered:
            return StateDerivativeEvaluationResult(
                0, 0.0, 0.0, 0.0, 0, self.spec.name
            )

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
            for index in range(1, len(items)):
                previous, current = items[index - 1], items[index]
                if self.require_consecutive and current.tick != previous.tick + 1:
                    continue
                prev = np.asarray(self.spec.feature(previous), dtype=float)
                curr = np.asarray(self.spec.feature(current), dtype=float)
                if prev.size != self.spec.width or curr.size != self.spec.width:
                    continue
                row = tuple(float(value) for value in (curr - prev))
                delta = current.coherence - previous.coherence
                if current.tick < heldout:
                    train_x.append(row)
                    train_y.append(delta)
                else:
                    test_x.append(row)
                    test_y.append(delta)

        if not train_x or not test_x:
            return StateDerivativeEvaluationResult(
                0, 0.0, 0.0, 0.0, heldout, self.spec.name
            )

        train = np.asarray(train_x, dtype=float)
        test = np.asarray(test_x, dtype=float)
        target = np.asarray(train_y, dtype=float)
        mean = train.mean(axis=0)
        scale = train.std(axis=0)
        scale[scale == 0.0] = 1.0

        design = np.column_stack((np.ones(len(train)), (train - mean) / scale))
        regularizer = np.eye(design.shape[1])
        regularizer[0, 0] = 0.0
        coef = np.linalg.solve(
            design.T @ design + self.ridge * regularizer,
            design.T @ target,
        )

        prediction = np.column_stack(
            (np.ones(len(test)), (test - mean) / scale)
        ) @ coef
        shuffled = test.copy()
        np.random.default_rng(390001).shuffle(shuffled)
        shuffled_prediction = np.column_stack(
            (np.ones(len(shuffled)), (shuffled - mean) / scale)
        ) @ coef

        actual = np.asarray(test_y, dtype=float)
        return StateDerivativeEvaluationResult(
            samples=len(actual),
            zero_mae=float(np.mean(np.abs(actual))),
            derivative_mae=float(np.mean(np.abs(actual - prediction))),
            shuffled_mae=float(np.mean(np.abs(actual - shuffled_prediction))),
            heldout_start_tick=heldout,
            feature_name=self.spec.name,
        )
