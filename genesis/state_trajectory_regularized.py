from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np

from .memory import MemoryRecord
from .state_innovation import STATE_FEATURES_WITH_COMBINED, StateFeatureSpec


@dataclass(frozen=True)
class RegularizedTrajectoryEvaluationResult:
    samples: int
    zero_mae: float
    trajectory_mae: float
    shuffled_mae: float
    heldout_start_tick: int
    feature_name: str
    history_length: int
    ridge: float

    @property
    def improvement(self) -> float:
        return self.zero_mae - self.trajectory_mae

    @property
    def beats_zero(self) -> bool:
        return self.trajectory_mae < self.zero_mae

    @property
    def beats_shuffled(self) -> bool:
        return self.trajectory_mae < self.shuffled_mae


class RegularizedStateTrajectoryPredictor:
    """GENESIS-2.13: choose ridge strength on an inner chronological validation split."""

    def __init__(
        self,
        feature_name: str = "combined",
        history_length: int = 3,
        train_fraction: float = 0.5,
        validation_fraction: float = 0.25,
        ridges: tuple[float, ...] = (1e-6, 1e-4, 1e-2, 1.0, 100.0, 10_000.0),
        require_consecutive: bool = True,
    ) -> None:
        if history_length < 2:
            raise ValueError("history_length must be >= 2")
        if not 0.0 < train_fraction < 1.0:
            raise ValueError("train_fraction must be between 0 and 1")
        if not 0.0 < validation_fraction < 1.0:
            raise ValueError("validation_fraction must be between 0 and 1")
        if not ridges or any(r < 0.0 for r in ridges):
            raise ValueError("ridges must contain non-negative values")
        matches = [s for s in STATE_FEATURES_WITH_COMBINED if s.name == feature_name]
        if not matches:
            raise ValueError(f"unknown state feature: {feature_name}")
        self.spec: StateFeatureSpec = matches[0]
        self.history_length = history_length
        self.train_fraction = train_fraction
        self.validation_fraction = validation_fraction
        self.ridges = tuple(ridges)
        self.require_consecutive = require_consecutive

    @staticmethod
    def _fit_predict(train_x, train_y, test_x, ridge):
        train = np.asarray(train_x, dtype=np.float64)
        test = np.asarray(test_x, dtype=np.float64)
        y = np.asarray(train_y, dtype=np.float64)
        mean = train.mean(0)
        scale = train.std(0)
        scale[scale == 0.0] = 1.0
        x = np.column_stack((np.ones(len(train)), (train - mean) / scale))
        v = np.column_stack((np.ones(len(test)), (test - mean) / scale))
        reg = np.eye(x.shape[1])
        reg[0, 0] = 0.0
        coef = np.linalg.solve(x.T @ x + ridge * reg, x.T @ y)
        return v @ coef

    def _samples(self, records):
        ordered = sorted(records, key=lambda item: (item.tick, item.identity))
        by_identity: dict[int, list[MemoryRecord]] = {}
        for item in ordered:
            by_identity.setdefault(item.identity, []).append(item)

        rows = []
        for items in by_identity.values():
            items.sort(key=lambda item: item.tick)
            for i in range(self.history_length, len(items)):
                window = items[i - self.history_length:i]
                target = items[i]
                ticks = [x.tick for x in window] + [target.tick]
                if self.require_consecutive and any(
                    ticks[j + 1] != ticks[j] + 1 for j in range(len(ticks) - 1)
                ):
                    continue
                vectors = [
                    tuple(float(v) for v in self.spec.feature(x))
                    for x in window
                ]
                if any(len(v) != self.spec.width for v in vectors):
                    continue
                rows.append((
                    tuple(v for vector in vectors for v in vector),
                    target.coherence - window[-1].coherence,
                    target.tick,
                ))
        return rows

    def evaluate(self, records: Iterable[MemoryRecord]) -> RegularizedTrajectoryEvaluationResult:
        rows = self._samples(records)
        if not rows:
            return RegularizedTrajectoryEvaluationResult(
                0, 0.0, 0.0, 0.0, 0, self.spec.name,
                self.history_length, self.ridges[0],
            )

        min_tick = min(r[2] for r in rows)
        max_tick = max(r[2] for r in rows)
        heldout = min_tick + max(1, int((max_tick - min_tick) * self.train_fraction))
        rows.sort(key=lambda row: row[2])
        train_rows = [r for r in rows if r[2] < heldout]
        test_rows = [r for r in rows if r[2] >= heldout]
        if len(train_rows) < 4 or not test_rows:
            return RegularizedTrajectoryEvaluationResult(
                0, 0.0, 0.0, 0.0, heldout, self.spec.name,
                self.history_length, self.ridges[0],
            )

        split = max(2, int(len(train_rows) * (1.0 - self.validation_fraction)))
        fit_rows, val_rows = train_rows[:split], train_rows[split:]
        if not val_rows:
            return RegularizedTrajectoryEvaluationResult(
                0, 0.0, 0.0, 0.0, heldout, self.spec.name,
                self.history_length, self.ridges[0],
            )

        fit_x = [r[0] for r in fit_rows]
        fit_y = [r[1] for r in fit_rows]
        val_x = [r[0] for r in val_rows]
        val_y = np.asarray([r[1] for r in val_rows], dtype=np.float64)

        scores = []
        for ridge in self.ridges:
            pred = self._fit_predict(fit_x, fit_y, val_x, ridge)
            scores.append((float(np.mean(np.abs(val_y - pred))), ridge))
        _, best_ridge = min(scores, key=lambda item: (item[0], item[1]))

        train_x = [r[0] for r in train_rows]
        train_y = [r[1] for r in train_rows]
        test_x = [r[0] for r in test_rows]
        actual = np.asarray([r[1] for r in test_rows], dtype=np.float64)

        pred = self._fit_predict(train_x, train_y, test_x, best_ridge)
        shuffled_x = np.asarray(test_x, dtype=np.float64).copy()
        np.random.default_rng(390001).shuffle(shuffled_x)
        shuffled = self._fit_predict(train_x, train_y, shuffled_x, best_ridge)

        return RegularizedTrajectoryEvaluationResult(
            samples=len(actual),
            zero_mae=float(np.mean(np.abs(actual))),
            trajectory_mae=float(np.mean(np.abs(actual - pred))),
            shuffled_mae=float(np.mean(np.abs(actual - shuffled))),
            heldout_start_tick=heldout,
            feature_name=self.spec.name,
            history_length=self.history_length,
            ridge=float(best_ridge),
        )
