from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np

from .memory import MemoryRecord
from .state_innovation import combined_state


@dataclass(frozen=True)
class NonlinearStateEvaluationResult:
    samples: int
    zero_mae: float
    nonlinear_mae: float
    shuffled_mae: float
    heldout_start_tick: int

    @property
    def improvement(self) -> float:
        return self.zero_mae - self.nonlinear_mae

    @property
    def beats_zero(self) -> bool:
        return self.nonlinear_mae < self.zero_mae

    @property
    def beats_shuffled(self) -> bool:
        return self.nonlinear_mae < self.shuffled_mae


class NonlinearStatePredictor:
    """Deterministic nonlinear control for current combined observer state.

    The universe and observer are unchanged. A fixed random tanh feature map
    is used only to test whether the linear-model class is the bottleneck.
    """

    def __init__(
        self,
        feature_count: int = 64,
        ridge: float = 1e-3,
        seed: int = 390001,
        train_fraction: float = 0.5,
        require_consecutive: bool = True,
    ) -> None:
        if feature_count < 1:
            raise ValueError("feature_count must be >= 1")
        if ridge < 0.0:
            raise ValueError("ridge must be >= 0")
        if not 0.0 < train_fraction < 1.0:
            raise ValueError("train_fraction must be between 0 and 1")
        self.feature_count = feature_count
        self.ridge = ridge
        self.seed = seed
        self.train_fraction = train_fraction
        self.require_consecutive = require_consecutive

    def evaluate(self, records: Iterable[MemoryRecord]) -> NonlinearStateEvaluationResult:
        ordered = sorted(records, key=lambda item: (item.tick, item.identity))
        if not ordered:
            return NonlinearStateEvaluationResult(0, 0.0, 0.0, 0.0, 0)

        lo, hi = ordered[0].tick, ordered[-1].tick
        heldout = lo + max(1, int((hi - lo) * self.train_fraction))
        groups: dict[int, list[MemoryRecord]] = {}
        for item in ordered:
            groups.setdefault(item.identity, []).append(item)

        train_x: list[tuple[float, ...]] = []
        train_y: list[float] = []
        test_x: list[tuple[float, ...]] = []
        test_y: list[float] = []

        for items in groups.values():
            items.sort(key=lambda item: item.tick)
            for current, target in zip(items, items[1:]):
                if self.require_consecutive and target.tick != current.tick + 1:
                    continue
                row = combined_state(current)
                if target.tick < heldout:
                    train_x.append(row)
                    train_y.append(target.coherence - current.coherence)
                else:
                    test_x.append(row)
                    test_y.append(target.coherence - current.coherence)

        if not train_x or not test_x:
            return NonlinearStateEvaluationResult(0, 0.0, 0.0, 0.0, heldout)

        train = np.asarray(train_x, dtype=np.float64)
        test = np.asarray(test_x, dtype=np.float64)
        y = np.asarray(train_y, dtype=np.float64)

        mean = train.mean(axis=0)
        scale = train.std(axis=0)
        scale[scale == 0.0] = 1.0
        train = (train - mean) / scale
        test = (test - mean) / scale

        rng = np.random.default_rng(self.seed)
        weights = rng.normal(0.0, 1.0 / np.sqrt(train.shape[1]), (train.shape[1], self.feature_count))
        bias = rng.uniform(-np.pi, np.pi, self.feature_count)

        def design(x: np.ndarray) -> np.ndarray:
            hidden = np.tanh(x @ weights + bias)
            return np.column_stack((np.ones(len(x)), hidden))

        x_train = design(train)
        x_test = design(test)
        regularizer = np.eye(x_train.shape[1])
        regularizer[0, 0] = 0.0
        coef = np.linalg.solve(
            x_train.T @ x_train + self.ridge * regularizer,
            x_train.T @ y,
        )
        prediction = x_test @ coef

        shuffled = test.copy()
        np.random.default_rng(self.seed).shuffle(shuffled)
        shuffled_prediction = design(shuffled) @ coef

        actual = np.asarray(test_y, dtype=np.float64)
        return NonlinearStateEvaluationResult(
            len(actual),
            float(np.mean(np.abs(actual))),
            float(np.mean(np.abs(actual - prediction))),
            float(np.mean(np.abs(actual - shuffled_prediction))),
            heldout,
        )
