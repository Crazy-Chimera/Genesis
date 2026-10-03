from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np

from .memory import MemoryRecord
from .state_innovation import STATE_FEATURES_WITH_COMBINED, StateFeatureSpec


@dataclass(frozen=True)
class CompressedStateTrajectoryEvaluationResult:
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
    """Predict coherence innovation from a PCA-compressed non-coherence state trajectory."""

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
            raise ValueError("components cannot exceed feature width")
        self.history_length = history_length
        self.components = components
        self.train_fraction = train_fraction
        self.ridge = ridge
        self.require_consecutive = require_consecutive

    def evaluate(
        self, records: Iterable[MemoryRecord]
    ) -> CompressedStateTrajectoryEvaluationResult:
        ordered = sorted(records, key=lambda item: (item.tick, item.identity))
        if not ordered:
            return CompressedStateTrajectoryEvaluationResult(
                0, 0.0, 0.0, 0.0, 0, self.spec.name,
                self.history_length, self.components,
            )

        lo, hi = ordered[0].tick, ordered[-1].tick
        heldout = lo + max(1, int((hi - lo) * self.train_fraction))
        groups: dict[int, list[MemoryRecord]] = {}
        for item in ordered:
            groups.setdefault(item.identity, []).append(item)

        train_windows: list[list[tuple[float, ...]]] = []
        train_y: list[float] = []
        test_windows: list[list[tuple[float, ...]]] = []
        test_y: list[float] = []

        for items in groups.values():
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
                    tuple(float(v) for v in self.spec.feature(item))
                    for item in window
                ]
                if any(len(v) != self.spec.width for v in vectors):
                    continue
                delta = target.coherence - window[-1].coherence
                if target.tick < heldout:
                    train_windows.append(vectors)
                    train_y.append(delta)
                else:
                    test_windows.append(vectors)
                    test_y.append(delta)

        if not train_windows or not test_windows:
            return CompressedStateTrajectoryEvaluationResult(
                0, 0.0, 0.0, 0.0, heldout, self.spec.name,
                self.history_length, self.components,
            )

        train_states = np.asarray(
            [state for window in train_windows for state in window], dtype=np.float64
        )
        mean = train_states.mean(axis=0)
        centered = train_states - mean
        covariance = (centered.T @ centered) / max(1, len(centered) - 1)
        eigenvalues, eigenvectors = np.linalg.eigh(covariance)
        basis = eigenvectors[:, np.argsort(eigenvalues)[::-1][: self.components]]

        def encode(windows: list[list[tuple[float, ...]]]) -> np.ndarray:
            rows = []
            for window in windows:
                latent = (np.asarray(window, dtype=np.float64) - mean) @ basis
                rows.append(latent.reshape(-1))
            return np.asarray(rows, dtype=np.float64)

        train = encode(train_windows)
        test = encode(test_windows)
        y = np.asarray(train_y, dtype=np.float64)

        x_mean = train.mean(axis=0)
        x_scale = train.std(axis=0)
        x_scale[x_scale == 0.0] = 1.0
        x = (train - x_mean) / x_scale
        v = (test - x_mean) / x_scale

        design = np.column_stack((np.ones(len(x)), x))
        regularizer = np.eye(design.shape[1])
        regularizer[0, 0] = 0.0
        coefficients = np.linalg.solve(
            design.T @ design + self.ridge * regularizer,
            design.T @ y,
        )
        prediction = np.column_stack((np.ones(len(v)), v)) @ coefficients

        shuffled = test.copy()
        np.random.default_rng(390001).shuffle(shuffled)
        shuffled_prediction = np.column_stack(
            (np.ones(len(shuffled)), (shuffled - x_mean) / x_scale)
        ) @ coefficients

        actual = np.asarray(test_y, dtype=np.float64)
        return CompressedStateTrajectoryEvaluationResult(
            len(actual),
            float(np.mean(np.abs(actual))),
            float(np.mean(np.abs(actual - prediction))),
            float(np.mean(np.abs(actual - shuffled_prediction))),
            heldout,
            self.spec.name,
            self.history_length,
            self.components,
        )
