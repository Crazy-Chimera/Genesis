from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np

from .memory import MemoryRecord
from .state_innovation import STATE_FEATURES_WITH_COMBINED


@dataclass(frozen=True)
class NonlinearStateInnovationEvaluationResult:
    samples: int
    zero_mae: float
    nonlinear_mae: float
    shuffled_mae: float
    heldout_start_tick: int
    feature_name: str
    random_features: int

    @property
    def improvement(self) -> float:
        return self.zero_mae - self.nonlinear_mae

    @property
    def beats_zero(self) -> bool:
        return self.nonlinear_mae < self.zero_mae

    @property
    def beats_shuffled(self) -> bool:
        return self.nonlinear_mae < self.shuffled_mae


class NonlinearStateInnovationPredictor:
    """Random Fourier-feature ridge probe using the same observer-state input."""

    def __init__(
        self,
        feature_name: str = "combined",
        random_features: int = 128,
        train_fraction: float = 0.5,
        ridge: float = 1e-3,
        bandwidth: float = 1.0,
        seed: int = 213001,
        require_consecutive: bool = True,
    ) -> None:
        if random_features < 1:
            raise ValueError("random_features must be >= 1")
        if not 0.0 < train_fraction < 1.0:
            raise ValueError("train_fraction must be between 0 and 1")
        if ridge < 0.0:
            raise ValueError("ridge must be >= 0")
        if bandwidth <= 0.0:
            raise ValueError("bandwidth must be > 0")
        matches = [s for s in STATE_FEATURES_WITH_COMBINED if s.name == feature_name]
        if not matches:
            raise ValueError(f"unknown state feature: {feature_name}")
        self.spec = matches[0]
        self.random_features = random_features
        self.train_fraction = train_fraction
        self.ridge = ridge
        self.bandwidth = bandwidth
        self.seed = seed
        self.require_consecutive = require_consecutive

    def _transform(self, values: np.ndarray, projection: np.ndarray, phase: np.ndarray) -> np.ndarray:
        normalized = (values - self._mean) / self._scale
        return np.sqrt(2.0 / self.random_features) * np.cos(
            normalized @ projection / self.bandwidth + phase
        )

    def evaluate(self, records: Iterable[MemoryRecord]) -> NonlinearStateInnovationEvaluationResult:
        ordered = sorted(records, key=lambda item: (item.tick, item.identity))
        if not ordered:
            return NonlinearStateInnovationEvaluationResult(
                0, 0.0, 0.0, 0.0, 0, self.spec.name, self.random_features
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
            for index in range(len(items) - 1):
                current, target = items[index], items[index + 1]
                if self.require_consecutive and target.tick != current.tick + 1:
                    continue
                row = tuple(float(v) for v in self.spec.feature(current))
                if len(row) != self.spec.width:
                    continue
                delta = target.coherence - current.coherence
                if target.tick < heldout:
                    train_x.append(row)
                    train_y.append(delta)
                else:
                    test_x.append(row)
                    test_y.append(delta)

        if not train_x or not test_x:
            return NonlinearStateInnovationEvaluationResult(
                0, 0.0, 0.0, 0.0, heldout, self.spec.name, self.random_features
            )

        train = np.asarray(train_x, dtype=np.float64)
        test = np.asarray(test_x, dtype=np.float64)
        target = np.asarray(train_y, dtype=np.float64)
        actual = np.asarray(test_y, dtype=np.float64)

        self._mean = train.mean(axis=0)
        self._scale = train.std(axis=0)
        self._scale[self._scale == 0.0] = 1.0

        rng = np.random.default_rng(self.seed)
        projection = rng.normal(0.0, 1.0, (self.spec.width, self.random_features))
        phase = rng.uniform(0.0, 2.0 * np.pi, self.random_features)

        features = self._transform(train, projection, phase)
        test_features = self._transform(test, projection, phase)
        design = np.column_stack((np.ones(len(features)), features))
        test_design = np.column_stack((np.ones(len(test_features)), test_features))

        regularizer = np.eye(design.shape[1])
        regularizer[0, 0] = 0.0
        coefficients = np.linalg.solve(
            design.T @ design + self.ridge * regularizer,
            design.T @ target,
        )
        prediction = test_design @ coefficients

        shuffled = test.copy()
        np.random.default_rng(self.seed).shuffle(shuffled)
        shuffled_features = self._transform(shuffled, projection, phase)
        shuffled_prediction = np.column_stack(
            (np.ones(len(shuffled_features)), shuffled_features)
        ) @ coefficients

        return NonlinearStateInnovationEvaluationResult(
            samples=len(actual),
            zero_mae=float(np.mean(np.abs(actual))),
            nonlinear_mae=float(np.mean(np.abs(actual - prediction))),
            shuffled_mae=float(np.mean(np.abs(actual - shuffled_prediction))),
            heldout_start_tick=heldout,
            feature_name=self.spec.name,
            random_features=self.random_features,
        )
