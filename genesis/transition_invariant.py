from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np

from .memory import MemoryRecord
from .state_innovation import combined_state


@dataclass(frozen=True)
class TransitionEvaluationResult:
    samples: int
    zero_mae: float
    transition_mae: float
    shuffled_mae: float
    heldout_start_tick: int
    transition_order: int

    @property
    def improvement(self) -> float:
        return self.zero_mae - self.transition_mae

    @property
    def beats_zero(self) -> bool:
        return self.transition_mae < self.zero_mae

    @property
    def beats_shuffled(self) -> bool:
        return self.transition_mae < self.shuffled_mae


def _transition_features(vectors: list[np.ndarray], order: int) -> np.ndarray:
    first = vectors[-1] - vectors[-2]
    features = [first, np.array([np.linalg.norm(first)])]
    if np.linalg.norm(vectors[-1]) and np.linalg.norm(vectors[-2]):
        cosine = float(
            np.dot(vectors[-1], vectors[-2])
            / (np.linalg.norm(vectors[-1]) * np.linalg.norm(vectors[-2]))
        )
    else:
        cosine = 0.0
    features.append(np.array([cosine]))
    if order >= 2:
        second = vectors[-1] - 2.0 * vectors[-2] + vectors[-3]
        features.extend((second, np.array([np.linalg.norm(second)])))
    return np.concatenate(features)


class TransitionInvariantPredictor:
    """Predict coherence innovation from compact non-coherence state transitions."""

    def __init__(
        self,
        transition_order: int = 1,
        train_fraction: float = 0.5,
        ridge: float = 1e-6,
        require_consecutive: bool = True,
    ) -> None:
        if transition_order not in (1, 2):
            raise ValueError("transition_order must be 1 or 2")
        if not 0.0 < train_fraction < 1.0:
            raise ValueError("train_fraction must be between 0 and 1")
        if ridge < 0.0:
            raise ValueError("ridge must be >= 0")
        self.transition_order = transition_order
        self.train_fraction = train_fraction
        self.ridge = ridge
        self.require_consecutive = require_consecutive

    def evaluate(self, records: Iterable[MemoryRecord]) -> TransitionEvaluationResult:
        ordered = sorted(records, key=lambda x: (x.tick, x.identity))
        if not ordered:
            return TransitionEvaluationResult(0, 0.0, 0.0, 0.0, 0, self.transition_order)

        lo, hi = ordered[0].tick, ordered[-1].tick
        heldout = lo + max(1, int((hi - lo) * self.train_fraction))
        groups: dict[int, list[MemoryRecord]] = {}
        for item in ordered:
            groups.setdefault(item.identity, []).append(item)

        train_x, train_y, test_x, test_y = [], [], [], []
        needed = self.transition_order + 1
        for items in groups.values():
            items.sort(key=lambda x: x.tick)
            for i in range(needed, len(items)):
                window = items[i-needed:i+1]
                ticks = [x.tick for x in window]
                if self.require_consecutive and any(
                    ticks[j + 1] != ticks[j] + 1 for j in range(len(ticks) - 1)
                ):
                    continue
                vectors = [np.asarray(combined_state(x), dtype=float) for x in window]
                row = _transition_features(vectors, self.transition_order)
                delta = window[-1].coherence - window[-2].coherence
                if window[-1].tick < heldout:
                    train_x.append(row)
                    train_y.append(delta)
                else:
                    test_x.append(row)
                    test_y.append(delta)

        if not train_x or not test_x:
            return TransitionEvaluationResult(0, 0.0, 0.0, 0.0, heldout, self.transition_order)

        train = np.asarray(train_x)
        test = np.asarray(test_x)
        y = np.asarray(train_y)
        mean = train.mean(0)
        scale = train.std(0)
        scale[scale == 0.0] = 1.0
        X = np.column_stack((np.ones(len(train)), (train - mean) / scale))
        V = np.column_stack((np.ones(len(test)), (test - mean) / scale))
        reg = np.eye(X.shape[1])
        reg[0, 0] = 0.0
        coef = np.linalg.solve(X.T @ X + self.ridge * reg, X.T @ y)
        pred = V @ coef

        shuffled = test.copy()
        np.random.default_rng(390001).shuffle(shuffled)
        shuffled_pred = np.column_stack(
            (np.ones(len(shuffled)), (shuffled - mean) / scale)
        ) @ coef
        actual = np.asarray(test_y)

        return TransitionEvaluationResult(
            len(actual),
            float(np.mean(np.abs(actual))),
            float(np.mean(np.abs(actual - pred))),
            float(np.mean(np.abs(actual - shuffled_pred))),
            heldout,
            self.transition_order,
        )
