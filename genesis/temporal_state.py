from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np

from .memory import MemoryRecord
from .state_innovation import STATE_FEATURES_WITH_COMBINED


@dataclass(frozen=True)
class TemporalStateEvaluationResult:
    samples: int
    zero_mae: float
    temporal_mae: float
    shuffled_mae: float
    heldout_start_tick: int
    feature_name: str
    mode: str
    history_length: int

    @property
    def improvement(self) -> float:
        return self.zero_mae - self.temporal_mae

    @property
    def beats_zero(self) -> bool:
        return self.temporal_mae < self.zero_mae

    @property
    def beats_shuffled(self) -> bool:
        return self.temporal_mae < self.shuffled_mae


class TemporalStatePredictor:
    """Predict next coherence innovation from temporal state invariants."""

    def __init__(
        self,
        feature_name: str = "combined",
        mode: str = "delta",
        history_length: int = 2,
        train_fraction: float = 0.5,
        ridge: float = 1e-6,
        require_consecutive: bool = True,
    ) -> None:
        if history_length < 2:
            raise ValueError("history_length must be >= 2")
        if mode not in {"delta", "acceleration", "summary"}:
            raise ValueError("unknown temporal mode")
        if mode == "acceleration" and history_length < 3:
            raise ValueError("acceleration requires history_length >= 3")
        if not 0.0 < train_fraction < 1.0:
            raise ValueError("train_fraction must be between 0 and 1")
        if ridge < 0.0:
            raise ValueError("ridge must be >= 0")
        matches = [s for s in STATE_FEATURES_WITH_COMBINED if s.name == feature_name]
        if not matches:
            raise ValueError(f"unknown state feature: {feature_name}")
        self.spec = matches[0]
        self.mode = mode
        self.history_length = history_length
        self.train_fraction = train_fraction
        self.ridge = ridge
        self.require_consecutive = require_consecutive

    def _vector(self, record: MemoryRecord) -> np.ndarray:
        values = np.asarray(self.spec.feature(record), dtype=np.float64)
        if values.size != self.spec.width:
            raise ValueError("feature width mismatch")
        return values

    def _row(self, window: list[MemoryRecord]) -> np.ndarray:
        states = [self._vector(item) for item in window]
        if self.mode == "delta":
            return states[-1] - states[-2]
        if self.mode == "acceleration":
            return states[-1] - 2.0 * states[-2] + states[-3]

        stacked = np.stack(states)
        return np.concatenate(
            (
                stacked[-1],
                stacked.mean(axis=0),
                stacked.std(axis=0),
                stacked[-1] - stacked[0],
            )
        )

    def evaluate(self, records: Iterable[MemoryRecord]) -> TemporalStateEvaluationResult:
        ordered = sorted(records, key=lambda item: (item.tick, item.identity))
        if not ordered:
            return TemporalStateEvaluationResult(
                0, 0.0, 0.0, 0.0, 0, self.spec.name, self.mode, self.history_length
            )

        min_tick, max_tick = ordered[0].tick, ordered[-1].tick
        heldout = min_tick + max(1, int((max_tick - min_tick) * self.train_fraction))
        groups: dict[int, list[MemoryRecord]] = {}
        for item in ordered:
            groups.setdefault(item.identity, []).append(item)

        train_x: list[np.ndarray] = []
        train_y: list[float] = []
        test_x: list[np.ndarray] = []
        test_y: list[float] = []

        for items in groups.values():
            items.sort(key=lambda item: item.tick)
            for index in range(self.history_length, len(items)):
                window = items[index - self.history_length : index]
                target = items[index]
                ticks = [item.tick for item in window] + [target.tick]
                if self.require_consecutive and any(
                    ticks[j + 1] != ticks[j] + 1 for j in range(len(ticks) - 1)
                ):
                    continue
                row = self._row(window)
                delta = target.coherence - window[-1].coherence
                if target.tick < heldout:
                    train_x.append(row)
                    train_y.append(delta)
                else:
                    test_x.append(row)
                    test_y.append(delta)

        if not train_x or not test_x:
            return TemporalStateEvaluationResult(
                0, 0.0, 0.0, 0.0, heldout, self.spec.name, self.mode, self.history_length
            )

        train = np.asarray(train_x)
        test = np.asarray(test_x)
        y = np.asarray(train_y)
        actual = np.asarray(test_y)

        mean = train.mean(axis=0)
        scale = train.std(axis=0)
        scale[scale == 0.0] = 1.0
        x = np.column_stack((np.ones(len(train)), (train - mean) / scale))
        v = np.column_stack((np.ones(len(test)), (test - mean) / scale))

        regularizer = np.eye(x.shape[1])
        regularizer[0, 0] = 0.0
        coefficients = np.linalg.solve(
            x.T @ x + self.ridge * regularizer,
            x.T @ y,
        )
        prediction = v @ coefficients

        shuffled = test.copy()
        np.random.default_rng(390001).shuffle(shuffled)
        shuffled_prediction = np.column_stack(
            (np.ones(len(shuffled)), (shuffled - mean) / scale)
        ) @ coefficients

        return TemporalStateEvaluationResult(
            samples=len(actual),
            zero_mae=float(np.mean(np.abs(actual))),
            temporal_mae=float(np.mean(np.abs(actual - prediction))),
            shuffled_mae=float(np.mean(np.abs(actual - shuffled_prediction))),
            heldout_start_tick=heldout,
            feature_name=self.spec.name,
            mode=self.mode,
            history_length=self.history_length,
        )
