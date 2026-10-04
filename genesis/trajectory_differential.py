from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np

from .memory import MemoryRecord
from .state_innovation import combined_state


@dataclass(frozen=True)
class TrajectoryDifferentialEvaluationResult:
    samples: int
    zero_mae: float
    differential_mae: float
    shuffled_mae: float
    heldout_start_tick: int
    history_length: int

    @property
    def improvement(self) -> float:
        return self.zero_mae - self.differential_mae

    @property
    def beats_zero(self) -> bool:
        return self.differential_mae < self.zero_mae

    @property
    def beats_shuffled(self) -> bool:
        return self.differential_mae < self.shuffled_mae


def _summary(previous: np.ndarray, current: np.ndarray) -> tuple[float, ...]:
    delta = current - previous
    prev_norm = float(np.linalg.norm(previous))
    cur_norm = float(np.linalg.norm(current))
    delta_norm = float(np.linalg.norm(delta))
    denom = prev_norm * cur_norm
    cosine = float(previous @ current / denom) if denom else 0.0
    return (
        float(np.mean(delta)),
        float(np.mean(np.abs(delta))),
        float(np.std(delta)),
        delta_norm,
        abs(cur_norm - prev_norm),
        cosine,
    )


def differential_trajectory(
    records: list[MemoryRecord], history_length: int
) -> tuple[float, ...]:
    vectors = [np.asarray(combined_state(record), dtype=np.float64) for record in records]
    values: list[float] = []
    for index in range(1, len(vectors)):
        values.extend(_summary(vectors[index - 1], vectors[index]))
    if len(vectors) >= 3:
        second = vectors[-1] - 2.0 * vectors[-2] + vectors[-3]
        values.extend(
            (
                float(np.mean(second)),
                float(np.mean(np.abs(second))),
                float(np.linalg.norm(second)),
            )
        )
    else:
        values.extend((0.0, 0.0, 0.0))
    return tuple(values[-(6 * (history_length - 1) + 3) :])


class TrajectoryDifferentialPredictor:
    """Predict next coherence innovation from compact state-motion summaries."""

    def __init__(
        self,
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
        self.history_length = history_length
        self.train_fraction = train_fraction
        self.ridge = ridge
        self.require_consecutive = require_consecutive

    def evaluate(
        self, records: Iterable[MemoryRecord]
    ) -> TrajectoryDifferentialEvaluationResult:
        ordered = sorted(records, key=lambda item: (item.tick, item.identity))
        if not ordered:
            return TrajectoryDifferentialEvaluationResult(
                0, 0.0, 0.0, 0.0, 0, self.history_length
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
            for index in range(self.history_length, len(items)):
                window = items[index - self.history_length : index]
                target = items[index]
                ticks = [item.tick for item in window] + [target.tick]
                if self.require_consecutive and any(
                    ticks[i + 1] != ticks[i] + 1 for i in range(len(ticks) - 1)
                ):
                    continue
                row = differential_trajectory(window, self.history_length)
                delta = target.coherence - window[-1].coherence
                if target.tick < heldout:
                    train_x.append(row)
                    train_y.append(delta)
                else:
                    test_x.append(row)
                    test_y.append(delta)

        if not train_x or not test_x:
            return TrajectoryDifferentialEvaluationResult(
                0, 0.0, 0.0, 0.0, heldout, self.history_length
            )

        train = np.asarray(train_x, dtype=np.float64)
        test = np.asarray(test_x, dtype=np.float64)
        y = np.asarray(train_y, dtype=np.float64)
        mean = train.mean(axis=0)
        scale = train.std(axis=0)
        scale[scale == 0.0] = 1.0
        design = np.column_stack((np.ones(len(train)), (train - mean) / scale))
        regularizer = np.eye(design.shape[1])
        regularizer[0, 0] = 0.0
        coef = np.linalg.solve(
            design.T @ design + self.ridge * regularizer,
            design.T @ y,
        )
        pred = np.column_stack(
            (np.ones(len(test)), (test - mean) / scale)
        ) @ coef

        shuffled = test.copy()
        np.random.default_rng(390001).shuffle(shuffled)
        shuffled_pred = np.column_stack(
            (np.ones(len(shuffled)), (shuffled - mean) / scale)
        ) @ coef
        actual = np.asarray(test_y, dtype=np.float64)

        return TrajectoryDifferentialEvaluationResult(
            len(actual),
            float(np.mean(np.abs(actual))),
            float(np.mean(np.abs(actual - pred))),
            float(np.mean(np.abs(actual - shuffled_pred))),
            heldout,
            self.history_length,
        )
