from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np

from .memory import MemoryRecord
from .state_innovation import STATE_FEATURES_WITH_COMBINED, StateFeatureSpec


@dataclass(frozen=True)
class CompressedTrajectoryEvaluationResult:
    samples: int
    zero_mae: float
    trajectory_mae: float
    shuffled_mae: float
    heldout_start_tick: int
    feature_name: str
    history_length: int
    components: int

    @property
    def improvement(self) -> float:
        return self.zero_mae - self.trajectory_mae

    @property
    def beats_zero(self) -> bool:
        return self.trajectory_mae < self.zero_mae

    @property
    def beats_shuffled(self) -> bool:
        return self.trajectory_mae < self.shuffled_mae


class CompressedStateTrajectoryPredictor:
    """Predict next coherence innovation from a PCA-compressed state trajectory.

    PCA is fit only on the chronological training set, preventing test leakage.
    """

    def __init__(
        self,
        feature_name: str = "combined",
        history_length: int = 3,
        components: int = 8,
        train_fraction: float = 0.5,
        ridge: float = 1e-6,
        require_consecutive: bool = True,
    ) -> None:
        if history_length < 2:
            raise ValueError("history_length must be >= 2")
        if components < 1:
            raise ValueError("components must be >= 1")
        if not 0.0 < train_fraction < 1.0:
            raise ValueError("train_fraction must be between 0 and 1")
        if ridge < 0.0:
            raise ValueError("ridge must be >= 0")
        matches = [s for s in STATE_FEATURES_WITH_COMBINED if s.name == feature_name]
        if not matches:
            raise ValueError(f"unknown state feature: {feature_name}")
        self.spec: StateFeatureSpec = matches[0]
        if components > self.spec.width:
            raise ValueError("components must not exceed feature width")
        self.history_length = history_length
        self.components = components
        self.train_fraction = train_fraction
        self.ridge = ridge
        self.require_consecutive = require_consecutive

    def evaluate(
        self, records: Iterable[MemoryRecord]
    ) -> CompressedTrajectoryEvaluationResult:
        ordered = sorted(records, key=lambda x: (x.tick, x.identity))
        if not ordered:
            return CompressedTrajectoryEvaluationResult(
                0, 0.0, 0.0, 0.0, 0, self.spec.name,
                self.history_length, self.components,
            )

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
            items.sort(key=lambda x: x.tick)
            for i in range(self.history_length, len(items)):
                window = items[i - self.history_length:i]
                target = items[i]
                ticks = [x.tick for x in window] + [target.tick]
                if self.require_consecutive and any(
                    ticks[j + 1] != ticks[j] + 1 for j in range(len(ticks) - 1)
                ):
                    continue
                vectors = [
                    tuple(float(v) for v in self.spec.feature(x)) for x in window
                ]
                if any(len(v) != self.spec.width for v in vectors):
                    continue
                row = tuple(v for vec in vectors for v in vec)
                delta = target.coherence - window[-1].coherence
                if target.tick < heldout:
                    train_x.append(row)
                    train_y.append(delta)
                else:
                    test_x.append(row)
                    test_y.append(delta)

        if not train_x or not test_x:
            return CompressedTrajectoryEvaluationResult(
                0, 0.0, 0.0, 0.0, heldout, self.spec.name,
                self.history_length, self.components,
            )

        train = np.asarray(train_x, dtype=np.float64)
        test = np.asarray(test_x, dtype=np.float64)
        y = np.asarray(train_y, dtype=np.float64)

        mean = train.mean(axis=0)
        scale = train.std(axis=0)
        scale[scale == 0.0] = 1.0
        train_scaled = (train - mean) / scale
        test_scaled = (test - mean) / scale

        # PCA basis is derived exclusively from training observations.
        _, singular_values, vt = np.linalg.svd(
            train_scaled, full_matrices=False
        )
        rank = min(self.components, vt.shape[0])
        basis = vt[:rank]
        train_pca = train_scaled @ basis.T
        test_pca = test_scaled @ basis.T

        design = np.column_stack((np.ones(len(train_pca)), train_pca))
        regularizer = np.eye(design.shape[1])
        regularizer[0, 0] = 0.0
        coefficients = np.linalg.solve(
            design.T @ design + self.ridge * regularizer,
            design.T @ y,
        )

        prediction = np.column_stack(
            (np.ones(len(test_pca)), test_pca)
        ) @ coefficients

        shuffled = test_pca.copy()
        np.random.default_rng(390001).shuffle(shuffled)
        shuffled_prediction = np.column_stack(
            (np.ones(len(shuffled)), shuffled)
        ) @ coefficients

        actual = np.asarray(test_y, dtype=np.float64)
        return CompressedTrajectoryEvaluationResult(
            samples=len(actual),
            zero_mae=float(np.mean(np.abs(actual))),
            trajectory_mae=float(np.mean(np.abs(actual - prediction))),
            shuffled_mae=float(np.mean(np.abs(actual - shuffled_prediction))),
            heldout_start_tick=heldout,
            feature_name=self.spec.name,
            history_length=self.history_length,
            components=rank,
        )
