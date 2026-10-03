from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np

from .memory import MemoryRecord


@dataclass(frozen=True)
class MotionEvaluationResult:
    samples: int
    baseline_mae: float
    motion_mae: float
    shuffled_mae: float
    heldout_start_tick: int

    @property
    def improvement(self) -> float:
        return self.baseline_mae - self.motion_mae

    @property
    def beats_baseline(self) -> bool:
        return self.motion_mae < self.baseline_mae


class MotionPredictor:
    """Predict next coherence from the previous region's measured motion."""

    def __init__(self, train_fraction: float = 0.5, ridge: float = 1e-6, require_consecutive: bool = True) -> None:
        if not 0.0 < train_fraction < 1.0:
            raise ValueError("train_fraction must be between 0 and 1")
        if ridge < 0.0:
            raise ValueError("ridge must be >= 0")
        self.train_fraction = train_fraction
        self.ridge = ridge
        self.require_consecutive = require_consecutive

    def evaluate(self, records: Iterable[MemoryRecord]) -> MotionEvaluationResult:
        ordered = sorted(records, key=lambda item: (item.tick, item.identity))
        if not ordered:
            return MotionEvaluationResult(0, 0.0, 0.0, 0.0, 0)
        min_tick, max_tick = ordered[0].tick, ordered[-1].tick
        heldout_start = min_tick + max(1, int((max_tick - min_tick) * self.train_fraction))
        by_identity: dict[int, list[MemoryRecord]] = {}
        for item in ordered:
            by_identity.setdefault(item.identity, []).append(item)

        train_rows: list[tuple[float, ...]] = []
        train_targets: list[float] = []
        test_rows: list[tuple[float, ...]] = []
        test_targets: list[float] = []
        baseline_errors: list[float] = []

        for identity_records in by_identity.values():
            identity_records.sort(key=lambda item: item.tick)
            for index in range(1, len(identity_records)):
                previous, target = identity_records[index - 1], identity_records[index]
                if self.require_consecutive and target.tick != previous.tick + 1:
                    continue
                if len(previous.motion) != 3:
                    continue
                row = tuple(previous.motion)
                if target.tick < heldout_start:
                    train_rows.append(row)
                    train_targets.append(target.coherence)
                else:
                    test_rows.append(row)
                    test_targets.append(target.coherence)
                    baseline_errors.append(abs(target.coherence - previous.coherence))

        if not train_rows or not test_rows:
            return MotionEvaluationResult(0, 0.0, 0.0, 0.0, heldout_start)

        train = np.asarray(train_rows, dtype=np.float64)
        test = np.asarray(test_rows, dtype=np.float64)
        targets = np.asarray(test_targets, dtype=np.float64)
        mean, scale = train.mean(axis=0), train.std(axis=0)
        scale[scale == 0.0] = 1.0
        train_n, test_n = (train - mean) / scale, (test - mean) / scale
        x_train = np.column_stack((np.ones(len(train_n)), train_n))
        x_test = np.column_stack((np.ones(len(test_n)), test_n))
        regularizer = np.eye(x_train.shape[1], dtype=np.float64)
        regularizer[0, 0] = 0.0
        coefficients = np.linalg.solve(
            x_train.T @ x_train + self.ridge * regularizer,
            x_train.T @ np.asarray(train_targets, dtype=np.float64),
        )
        predictions = x_test @ coefficients
        shuffled = test.copy()
        np.random.default_rng(390001).shuffle(shuffled)
        shuffled_n = (shuffled - mean) / scale
        shuffled_predictions = np.column_stack((np.ones(len(shuffled_n)), shuffled_n)) @ coefficients

        return MotionEvaluationResult(
            samples=len(targets),
            baseline_mae=float(np.mean(baseline_errors)),
            motion_mae=float(np.mean(np.abs(targets - predictions))),
            shuffled_mae=float(np.mean(np.abs(targets - shuffled_predictions))),
            heldout_start_tick=heldout_start,
        )
