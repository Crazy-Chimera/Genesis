from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np

from .memory import MemoryRecord
from .state_innovation import STATE_FEATURES_WITH_COMBINED


@dataclass(frozen=True)
class PCAInnovationEvaluationResult:
    samples: int
    zero_mae: float
    state_mae: float
    shuffled_mae: float
    heldout_start_tick: int
    components: int

    @property
    def improvement(self) -> float:
        return self.zero_mae - self.state_mae

    @property
    def beats_zero(self) -> bool:
        return self.state_mae < self.zero_mae

    @property
    def beats_shuffled(self) -> bool:
        return self.state_mae < self.shuffled_mae


class PCAStateInnovationPredictor:
    """Predict next coherence innovation from a PCA-compressed non-coherence state."""

    def __init__(
        self,
        components: int = 16,
        train_fraction: float = 0.5,
        ridge: float = 1e-6,
        require_consecutive: bool = True,
    ) -> None:
        if components < 1 or components > 193:
            raise ValueError("components must be between 1 and 193")
        if not 0.0 < train_fraction < 1.0:
            raise ValueError("train_fraction must be between 0 and 1")
        if ridge < 0.0:
            raise ValueError("ridge must be >= 0")
        self.components = components
        self.train_fraction = train_fraction
        self.ridge = ridge
        self.require_consecutive = require_consecutive

    def evaluate(self, records: Iterable[MemoryRecord]) -> PCAInnovationEvaluationResult:
        ordered = sorted(records, key=lambda item: (item.tick, item.identity))
        if not ordered:
            return PCAInnovationEvaluationResult(0, 0.0, 0.0, 0.0, 0, self.components)

        min_tick, max_tick = ordered[0].tick, ordered[-1].tick
        heldout = min_tick + max(1, int((max_tick - min_tick) * self.train_fraction))
        spec = next(s for s in STATE_FEATURES_WITH_COMBINED if s.name == "combined")
        groups: dict[int, list[MemoryRecord]] = {}
        for item in ordered:
            groups.setdefault(item.identity, []).append(item)

        train_x, train_y, test_x, test_y = [], [], [], []
        for items in groups.values():
            items.sort(key=lambda x: x.tick)
            for current, target in zip(items, items[1:]):
                if self.require_consecutive and target.tick != current.tick + 1:
                    continue
                row = tuple(float(v) for v in spec.feature(current))
                delta = target.coherence - current.coherence
                (train_x if target.tick < heldout else test_x).append(row)
                (train_y if target.tick < heldout else test_y).append(delta)

        if not train_x or not test_x:
            return PCAInnovationEvaluationResult(0, 0.0, 0.0, 0.0, heldout, self.components)

        train = np.asarray(train_x, dtype=np.float64)
        test = np.asarray(test_x, dtype=np.float64)
        y = np.asarray(train_y, dtype=np.float64)
        actual = np.asarray(test_y, dtype=np.float64)

        mean = train.mean(axis=0)
        scale = train.std(axis=0)
        scale[scale == 0.0] = 1.0
        normalized = (train - mean) / scale
        covariance = (normalized.T @ normalized) / max(1, len(normalized) - 1)
        values, vectors = np.linalg.eigh(covariance)
        basis = vectors[:, np.argsort(values)[::-1][: self.components]]

        train_pca = normalized @ basis
        test_pca = ((test - mean) / scale) @ basis
        design = np.column_stack((np.ones(len(train_pca)), train_pca))
        regularizer = np.eye(design.shape[1])
        regularizer[0, 0] = 0.0
        coefficients = np.linalg.solve(
            design.T @ design + self.ridge * regularizer,
            design.T @ y,
        )
        prediction = np.column_stack((np.ones(len(test_pca)), test_pca)) @ coefficients

        shuffled = test_pca.copy()
        np.random.default_rng(390001).shuffle(shuffled)
        shuffled_prediction = np.column_stack((np.ones(len(shuffled)), shuffled)) @ coefficients

        return PCAInnovationEvaluationResult(
            len(actual),
            float(np.mean(np.abs(actual))),
            float(np.mean(np.abs(actual - prediction))),
            float(np.mean(np.abs(actual - shuffled_prediction))),
            heldout,
            self.components,
        )
