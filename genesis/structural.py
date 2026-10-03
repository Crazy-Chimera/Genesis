from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

import numpy as np

from .memory import MemoryRecord

STRUCTURAL_FEATURES = (
    "size",
    "boundary_contrast",
    "lifetime",
    "persistence",
    "overlap",
)


def structural_features(record: MemoryRecord) -> tuple[float, ...]:
    """Observer-measured structural features; coherence is deliberately excluded."""
    return (
        float(len(record.cells)),
        record.boundary_contrast,
        float(record.lifetime),
        float(record.persistence),
        record.overlap,
    )


@dataclass(frozen=True)
class StructuralEvaluationResult:
    """Out-of-sample evaluation of structure-only next-step prediction."""

    samples: int
    baseline_mae: float
    structural_mae: float
    shuffled_mae: float
    heldout_start_tick: int
    feature_names: tuple[str, ...] = STRUCTURAL_FEATURES

    @property
    def improvement(self) -> float:
        return self.baseline_mae - self.structural_mae

    @property
    def beats_baseline(self) -> bool:
        return self.structural_mae < self.baseline_mae

    @property
    def beats_shuffled(self) -> bool:
        return self.structural_mae < self.shuffled_mae


def _design(rows: Sequence[tuple[float, ...]]) -> np.ndarray:
    if not rows:
        return np.empty((0, 1), dtype=np.float64)
    values = np.asarray(rows, dtype=np.float64)
    scale = values.std(axis=0)
    scale[scale == 0.0] = 1.0
    normalized = (values - values.mean(axis=0)) / scale
    return np.column_stack((np.ones(len(rows)), normalized))


def _fit_ridge(rows: Sequence[tuple[float, ...]], targets: Sequence[float], ridge: float) -> np.ndarray:
    if not rows:
        raise ValueError("training rows must not be empty")
    if ridge < 0.0:
        raise ValueError("ridge must be >= 0")
    x = _design(rows)
    y = np.asarray(targets, dtype=np.float64)
    regularizer = np.eye(x.shape[1], dtype=np.float64)
    regularizer[0, 0] = 0.0
    return np.linalg.solve(x.T @ x + ridge * regularizer, x.T @ y)


def _predict(
    rows: Sequence[tuple[float, ...]],
    coefficients: np.ndarray,
    training_rows: Sequence[tuple[float, ...]],
) -> np.ndarray:
    if not rows:
        return np.empty(0, dtype=np.float64)
    train = np.asarray(training_rows, dtype=np.float64)
    values = np.asarray(rows, dtype=np.float64)
    mean = train.mean(axis=0)
    scale = train.std(axis=0)
    scale[scale == 0.0] = 1.0
    normalized = (values - mean) / scale
    x = np.column_stack((np.ones(len(rows)), normalized))
    return x @ coefficients


class StructuralPredictor:
    """Predict next coherence from measured structure, never from coherence history."""

    def __init__(
        self,
        train_fraction: float = 0.5,
        ridge: float = 1e-6,
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
        self,
        records: Iterable[MemoryRecord],
        feature_names: Sequence[str] = STRUCTURAL_FEATURES,
    ) -> StructuralEvaluationResult:
        names = tuple(feature_names)
        unknown = set(names) - set(STRUCTURAL_FEATURES)
        if not names or unknown:
            raise ValueError(f"unknown or empty structural feature set: {unknown}")

        indices = tuple(STRUCTURAL_FEATURES.index(name) for name in names)
        ordered = sorted(records, key=lambda item: (item.tick, item.identity))
        if not ordered:
            return StructuralEvaluationResult(0, 0.0, 0.0, 0.0, 0, names)

        min_tick = ordered[0].tick
        max_tick = ordered[-1].tick
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
                previous = identity_records[index - 1]
                target = identity_records[index]
                if self.require_consecutive and target.tick != previous.tick + 1:
                    continue
                features = structural_features(previous)
                row = tuple(features[i] for i in indices)
                if target.tick < heldout_start:
                    train_rows.append(row)
                    train_targets.append(target.coherence)
                else:
                    test_rows.append(row)
                    test_targets.append(target.coherence)
                    baseline_errors.append(abs(target.coherence - previous.coherence))

        if not train_rows or not test_rows:
            return StructuralEvaluationResult(0, 0.0, 0.0, 0.0, heldout_start, names)

        coefficients = _fit_ridge(train_rows, train_targets, self.ridge)
        predictions = _predict(test_rows, coefficients, train_rows)

        shuffled_rows = list(test_rows)
        rng = np.random.default_rng(390001)
        rng.shuffle(shuffled_rows)
        shuffled_predictions = _predict(shuffled_rows, coefficients, train_rows)

        actual = np.asarray(test_targets, dtype=np.float64)
        return StructuralEvaluationResult(
            samples=len(test_targets),
            baseline_mae=float(np.mean(baseline_errors)),
            structural_mae=float(np.mean(np.abs(actual - predictions))),
            shuffled_mae=float(np.mean(np.abs(actual - shuffled_predictions))),
            heldout_start_tick=heldout_start,
            feature_names=names,
        )
