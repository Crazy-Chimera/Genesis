from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np


@dataclass(frozen=True)
class GlobalPhaseEvaluationResult:
    samples: int
    zero_mae: float
    phase_mae: float
    shuffled_mae: float
    heldout_start_tick: int

    @property
    def improvement(self) -> float:
        return self.zero_mae - self.phase_mae

    @property
    def beats_zero(self) -> bool:
        return self.phase_mae < self.zero_mae

    @property
    def beats_shuffled(self) -> bool:
        return self.phase_mae < self.shuffled_mae


def phase_features(phase: np.ndarray) -> tuple[float, ...]:
    values = np.asarray(phase, dtype=np.float64)
    return tuple(np.concatenate((np.sin(values).ravel(), np.cos(values).ravel())))


class GlobalPhasePredictor:
    """Predict next coherence innovation from the full global phase state."""

    def __init__(
        self,
        train_fraction: float = 0.5,
        ridge: float = 1e-3,
        require_consecutive: bool = True,
    ) -> None:
        if not 0.0 < train_fraction < 1.0:
            raise ValueError("train_fraction must be between 0 and 1")
        if ridge < 0.0:
            raise ValueError("ridge must be >= 0")
        self.train_fraction = train_fraction
        self.ridge = ridge
        self.require_consecutive = require_consecutive

    def evaluate(
        self, records: Iterable[tuple[int, np.ndarray, float]]
    ) -> GlobalPhaseEvaluationResult:
        ordered = sorted(records, key=lambda item: item[0])
        if not ordered:
            return GlobalPhaseEvaluationResult(0, 0.0, 0.0, 0.0, 0)

        min_tick, max_tick = ordered[0][0], ordered[-1][0]
        heldout = min_tick + max(1, int((max_tick - min_tick) * self.train_fraction))

        train_x: list[tuple[float, ...]] = []
        train_y: list[float] = []
        test_x: list[tuple[float, ...]] = []
        test_y: list[float] = []

        for index in range(len(ordered) - 1):
            current = ordered[index]
            target = ordered[index + 1]
            if self.require_consecutive and target[0] != current[0] + 1:
                continue
            row = phase_features(current[1])
            delta = target[2] - current[2]
            if target[0] < heldout:
                train_x.append(row)
                train_y.append(delta)
            else:
                test_x.append(row)
                test_y.append(delta)

        if not train_x or not test_x:
            return GlobalPhaseEvaluationResult(0, 0.0, 0.0, 0.0, heldout)

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
        return GlobalPhaseEvaluationResult(
            samples=len(actual),
            zero_mae=float(np.mean(np.abs(actual))),
            phase_mae=float(np.mean(np.abs(actual - prediction))),
            shuffled_mae=float(np.mean(np.abs(actual - shuffled_prediction))),
            heldout_start_tick=heldout,
        )
