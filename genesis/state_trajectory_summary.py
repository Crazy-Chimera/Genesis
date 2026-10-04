from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np

from .memory import MemoryRecord
from .state_innovation import combined_state


def summarize_vectors(vectors: list[tuple[float, ...]]) -> tuple[float, ...]:
    """Compress a state trajectory into scale-normalized trajectory statistics."""
    if len(vectors) < 2:
        raise ValueError("at least two state vectors are required")

    x = np.asarray(vectors, dtype=np.float64)
    features: list[float] = []

    for row in x:
        features.extend(
            (
                float(np.mean(row)),
                float(np.std(row)),
                float(np.min(row)),
                float(np.max(row)),
                float(np.linalg.norm(row)),
            )
        )

    for previous, current in zip(x[:-1], x[1:]):
        delta = current - previous
        denom = float(np.linalg.norm(previous) * np.linalg.norm(current))
        cosine = float(previous @ current / denom) if denom else 0.0
        features.extend(
            (
                float(np.mean(delta)),
                float(np.std(delta)),
                float(np.linalg.norm(delta)),
                cosine,
            )
        )

    return tuple(features)


@dataclass(frozen=True)
class TrajectorySummaryEvaluationResult:
    samples: int
    zero_mae: float
    summary_mae: float
    shuffled_mae: float
    heldout_start_tick: int
    history_length: int

    @property
    def improvement(self) -> float:
        return self.zero_mae - self.summary_mae

    @property
    def beats_zero(self) -> bool:
        return self.summary_mae < self.zero_mae

    @property
    def beats_shuffled(self) -> bool:
        return self.summary_mae < self.shuffled_mae


class TrajectorySummaryPredictor:
    """Predict next coherence innovation from compressed non-coherence trajectory statistics."""

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
    ) -> TrajectorySummaryEvaluationResult:
        ordered = sorted(records, key=lambda item: (item.tick, item.identity))
        if not ordered:
            return TrajectorySummaryEvaluationResult(0, 0.0, 0.0, 0.0, 0, self.history_length)

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
                window = items[index - self.history_length : index]
                target = items[index]
                ticks = [item.tick for item in window] + [target.tick]
                if self.require_consecutive and any(
                    ticks[j + 1] != ticks[j] + 1 for j in range(len(ticks) - 1)
                ):
                    continue

                row = summarize_vectors([combined_state(item) for item in window])
                delta = target.coherence - window[-1].coherence
                if target.tick < heldout:
                    train_x.append(row)
                    train_y.append(delta)
                else:
                    test_x.append(row)
                    test_y.append(delta)

        if not train_x or not test_x:
            return TrajectorySummaryEvaluationResult(
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
        return TrajectorySummaryEvaluationResult(
            len(actual),
            float(np.mean(np.abs(actual))),
            float(np.mean(np.abs(actual - prediction))),
            float(np.mean(np.abs(actual - shuffled_prediction))),
            heldout,
            self.history_length,
        )
