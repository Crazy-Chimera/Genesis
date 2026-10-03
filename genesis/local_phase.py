from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np

from .memory import MemoryRecord


@dataclass(frozen=True)
class PhaseEvaluationResult:
    """Out-of-sample prediction from the previous local relative-phase patch."""

    samples: int
    baseline_mae: float
    phase_mae: float
    shuffled_mae: float
    heldout_start_tick: int
    radius: int

    @property
    def improvement(self) -> float:
        return self.baseline_mae - self.phase_mae

    @property
    def beats_baseline(self) -> bool:
        return self.phase_mae < self.baseline_mae

    @property
    def beats_shuffled(self) -> bool:
        return self.phase_mae < self.shuffled_mae


class PhasePatchPredictor:
    """Predict next coherence from the previous relative-phase patch only."""

    def __init__(
        self,
        train_fraction: float = 0.5,
        ridge: float = 1e-6,
        require_consecutive: bool = True,
        radius: int = 1,
    ) -> None:
        if not 0.0 < train_fraction < 1.0:
            raise ValueError("train_fraction must be between 0 and 1")
        if ridge < 0.0:
            raise ValueError("ridge must be >= 0")
        if radius < 0:
            raise ValueError("radius must be >= 0")
        self.train_fraction = train_fraction
        self.ridge = ridge
        self.require_consecutive = require_consecutive
        self.radius = radius

    def evaluate(self, records: Iterable[MemoryRecord]) -> PhaseEvaluationResult:
        ordered = sorted(records, key=lambda item: (item.tick, item.identity))
        if not ordered:
            return PhaseEvaluationResult(0, 0.0, 0.0, 0.0, 0, self.radius)

        min_tick = ordered[0].tick
        max_tick = ordered[-1].tick
        heldout_start = min_tick + max(1, int((max_tick - min_tick) * self.train_fraction))
        expected_width = 2 * (2 * self.radius + 1) ** 2

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
                previous = identity_records[index - 1]
                target = identity_records[index]
                if self.require_consecutive and target.tick != previous.tick + 1:
                    continue
                if len(previous.phase_patch) != expected_width:
                    continue
                row = tuple(previous.phase_patch)
                if target.tick < heldout_start:
                    train_rows.append(row)
                    train_targets.append(target.coherence)
                else:
                    test_rows.append(row)
                    test_targets.append(target.coherence)
                    baseline_errors.append(abs(target.coherence - previous.coherence))

        if not train_rows or not test_rows:
            return PhaseEvaluationResult(0, 0.0, 0.0, 0.0, heldout_start, self.radius)

        train = np.asarray(train_rows, dtype=np.float64)
        test = np.asarray(test_rows, dtype=np.float64)
        targets = np.asarray(test_targets, dtype=np.float64)

        mean = train.mean(axis=0)
        scale = train.std(axis=0)
        scale[scale == 0.0] = 1.0
        train_n = (train - mean) / scale
        test_n = (test - mean) / scale
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

        return PhaseEvaluationResult(
            samples=len(targets),
            baseline_mae=float(np.mean(baseline_errors)),
            phase_mae=float(np.mean(np.abs(targets - predictions))),
            shuffled_mae=float(np.mean(np.abs(targets - shuffled_predictions))),
            heldout_start_tick=heldout_start,
            radius=self.radius,
        )
