from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np

from .memory import MemoryRecord
from .state_innovation import STATE_FEATURES


@dataclass(frozen=True)
class StateChangeEvaluationResult:
    samples: int
    zero_mae: float
    change_mae: float
    shuffled_mae: float
    heldout_start_tick: int
    history_length: int

    @property
    def improvement(self) -> float:
        return self.zero_mae - self.change_mae

    @property
    def beats_zero(self) -> bool:
        return self.change_mae < self.zero_mae

    @property
    def beats_shuffled(self) -> bool:
        return self.change_mae < self.shuffled_mae


def _fixed_vector(values: Iterable[float], width: int) -> np.ndarray:
    vector = np.asarray(tuple(values), dtype=float)
    if vector.size > width:
        raise ValueError(f"feature width {vector.size} exceeds declared width {width}")
    if vector.size == width:
        return vector
    return np.pad(vector, (0, width - vector.size))


def state_change(previous: MemoryRecord, current: MemoryRecord) -> tuple[float, ...]:
    """Return compact, fixed-width statistics of measured feature changes.

    Missing observer values at a region birth are represented by zero displacement
    up to the feature's declared width. The universe is not modified.
    """
    values: list[float] = []
    for spec in STATE_FEATURES:
        before = _fixed_vector(spec.feature(previous), spec.width)
        after = _fixed_vector(spec.feature(current), spec.width)
        delta = after - before
        values.extend(
            (
                float(np.mean(delta)),
                float(np.std(delta)),
                float(np.mean(np.abs(delta))),
                float(np.max(np.abs(delta))) if delta.size else 0.0,
            )
        )
    return tuple(values)


class StateChangePredictor:
    """Predict next coherence innovation from compact state-change trajectories."""

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

    def evaluate(self, records: Iterable[MemoryRecord]) -> StateChangeEvaluationResult:
        ordered = sorted(records, key=lambda item: (item.tick, item.identity))
        if not ordered:
            return StateChangeEvaluationResult(0, 0.0, 0.0, 0.0, 0, self.history_length)

        min_tick, max_tick = ordered[0].tick, ordered[-1].tick
        heldout = min_tick + max(1, int((max_tick - min_tick) * self.train_fraction))
        by_identity: dict[int, list[MemoryRecord]] = {}
        for item in ordered:
            by_identity.setdefault(item.identity, []).append(item)

        train_x: list[tuple[float, ...]] = []
        train_y: list[float] = []
        test_x: list[tuple[float, ...]] = []
        test_y: list[float] = []

        for items in by_identity.values():
            items.sort(key=lambda item: item.tick)
            for index in range(self.history_length, len(items)):
                window = items[index - self.history_length:index]
                target = items[index]
                ticks = [item.tick for item in window] + [target.tick]
                if self.require_consecutive and any(
                    ticks[j + 1] != ticks[j] + 1 for j in range(len(ticks) - 1)
                ):
                    continue

                changes = [
                    state_change(window[j], window[j + 1])
                    for j in range(len(window) - 1)
                ]
                row = tuple(value for change in changes for value in change)
                delta = target.coherence - window[-1].coherence

                if target.tick < heldout:
                    train_x.append(row)
                    train_y.append(delta)
                else:
                    test_x.append(row)
                    test_y.append(delta)

        if not train_x or not test_x:
            return StateChangeEvaluationResult(
                0, 0.0, 0.0, 0.0, heldout, self.history_length
            )

        train = np.asarray(train_x, dtype=float)
        test = np.asarray(test_x, dtype=float)
        y = np.asarray(train_y, dtype=float)

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

        prediction = np.column_stack(
            (np.ones(len(test)), (test - mean) / scale)
        ) @ coef

        shuffled = test.copy()
        np.random.default_rng(390001).shuffle(shuffled)
        shuffled_prediction = np.column_stack(
            (np.ones(len(shuffled)), (shuffled - mean) / scale)
        ) @ coef

        actual = np.asarray(test_y, dtype=float)
        return StateChangeEvaluationResult(
            len(actual),
            float(np.mean(np.abs(actual))),
            float(np.mean(np.abs(actual - prediction))),
            float(np.mean(np.abs(actual - shuffled_prediction))),
            heldout,
            self.history_length,
        )
