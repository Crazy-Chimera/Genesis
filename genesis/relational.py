from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np

from .memory import MemoryRecord

RELATIONAL_WIDTH = 16


@dataclass(frozen=True)
class RelationalEvaluationResult:
    """Out-of-sample prediction from cross-region relations only."""

    samples: int
    baseline_mae: float
    relational_mae: float
    shuffled_mae: float
    heldout_start_tick: int

    @property
    def improvement(self) -> float:
        return self.baseline_mae - self.relational_mae

    @property
    def beats_baseline(self) -> bool:
        return self.relational_mae < self.baseline_mae

    @property
    def beats_shuffled(self) -> bool:
        return self.relational_mae < self.shuffled_mae


def _design(rows: list[tuple[float, ...]]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    values = np.asarray(rows, dtype=np.float64)
    mean = values.mean(axis=0)
    scale = values.std(axis=0)
    scale[scale == 0.0] = 1.0
    normalized = (values - mean) / scale
    return np.column_stack((np.ones(len(rows)), normalized)), mean, scale


class CrossRegionRelationalPredictor:
    """Predict next coherence from simultaneous peer-region relations only."""

    def __init__(
        self,
        max_peers: int = 2,
        train_fraction: float = 0.5,
        ridge: float = 1e-6,
        require_consecutive: bool = True,
    ) -> None:
        if max_peers < 1:
            raise ValueError("max_peers must be >= 1")
        if not 0.0 < train_fraction < 1.0:
            raise ValueError("train_fraction must be between 0 and 1")
        if ridge < 0.0:
            raise ValueError("ridge must be >= 0")
        self.max_peers = max_peers
        self.train_fraction = train_fraction
        self.ridge = ridge
        self.require_consecutive = require_consecutive

    def evaluate(self, records: Iterable[MemoryRecord]) -> RelationalEvaluationResult:
        ordered = sorted(records, key=lambda item: (item.tick, item.identity))
        if not ordered:
            return RelationalEvaluationResult(0, 0.0, 0.0, 0.0, 0)

        min_tick, max_tick = ordered[0].tick, ordered[-1].tick
        heldout = min_tick + max(1, int((max_tick - min_tick) * self.train_fraction))
        by_identity: dict[int, list[MemoryRecord]] = {}
        for item in ordered:
            by_identity.setdefault(item.identity, []).append(item)

        train_rows: list[tuple[float, ...]] = []
        train_targets: list[float] = []
        test_rows: list[tuple[float, ...]] = []
        test_targets: list[float] = []
        baseline_errors: list[float] = []

        for items in by_identity.values():
            items.sort(key=lambda item: item.tick)
            for index in range(1, len(items)):
                previous, target = items[index - 1], items[index]
                if self.require_consecutive and target.tick != previous.tick + 1:
                    continue
                if len(previous.relational) != self.max_peers * 8:
                    continue
                if target.tick < heldout:
                    train_rows.append(previous.relational)
                    train_targets.append(target.coherence)
                else:
                    test_rows.append(previous.relational)
                    test_targets.append(target.coherence)
                    baseline_errors.append(abs(target.coherence - previous.coherence))

        if not train_rows or not test_rows:
            return RelationalEvaluationResult(0, 0.0, 0.0, 0.0, heldout)

        x, mean, scale = _design(train_rows)
        y = np.asarray(train_targets, dtype=np.float64)
        regularizer = np.eye(x.shape[1], dtype=np.float64)
        regularizer[0, 0] = 0.0
        coefficients = np.linalg.solve(
            x.T @ x + self.ridge * regularizer,
            x.T @ y,
        )

        test = (np.asarray(test_rows, dtype=np.float64) - mean) / scale
        design_test = np.column_stack((np.ones(len(test)), test))
        prediction = design_test @ coefficients

        shuffled = np.asarray(test_rows, dtype=np.float64).copy()
        np.random.default_rng(390001).shuffle(shuffled)
        shuffled = (shuffled - mean) / scale
        shuffled_prediction = np.column_stack((np.ones(len(shuffled)), shuffled)) @ coefficients

        actual = np.asarray(test_targets, dtype=np.float64)
        return RelationalEvaluationResult(
            samples=len(actual),
            baseline_mae=float(np.mean(baseline_errors)),
            relational_mae=float(np.mean(np.abs(actual - prediction))),
            shuffled_mae=float(np.mean(np.abs(actual - shuffled_prediction))),
            heldout_start_tick=heldout,
        )
