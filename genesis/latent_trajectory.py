from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np

from .memory import MemoryRecord
from .state_innovation import STATE_FEATURES_WITH_COMBINED


@dataclass(frozen=True)
class LatentTrajectoryEvaluationResult:
    samples: int
    zero_mae: float
    trajectory_mae: float
    shuffled_mae: float
    heldout_start_tick: int
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


class LatentTrajectoryPredictor:
    """Predict next coherence innovation from PCA-compressed non-coherence state."""

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
        self.spec = matches[0]
        if components > self.spec.width:
            raise ValueError("components cannot exceed feature width")
        self.history_length = history_length
        self.components = components
        self.train_fraction = train_fraction
        self.ridge = ridge
        self.require_consecutive = require_consecutive

    def evaluate(self, records: Iterable[MemoryRecord]) -> LatentTrajectoryEvaluationResult:
        ordered = sorted(records, key=lambda x: (x.tick, x.identity))
        if not ordered:
            return LatentTrajectoryEvaluationResult(
                0, 0.0, 0.0, 0.0, 0, self.history_length, self.components
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
                delta = target.coherence - window[-1].coherence
                if target.tick < heldout:
                    train_windows.append(vectors)
                    train_y.append(delta)
                else:
                    test_windows.append(vectors)
                    test_y.append(delta)

        if not train_windows or not test_windows:
            return LatentTrajectoryEvaluationResult(
                0, 0.0, 0.0, 0.0, heldout, self.history_length, self.components
            )

        train_flat = np.asarray([v for w in train_windows for v in w], dtype=float)
        test_flat = np.asarray([v for w in test_windows for v in w], dtype=float)

        mean = train_flat.mean(axis=0)
        centered = train_flat - mean
        _, _, vt = np.linalg.svd(centered, full_matrices=False)
        basis = vt[: self.components]

        def encode(windows: list[list[tuple[float, ...]]]) -> np.ndarray:
            rows = []
            for window in windows:
                latent = [(np.asarray(v) - mean) @ basis.T for v in window]
                rows.append(np.concatenate(latent))
            return np.asarray(rows, dtype=float)

        train_x = encode(train_windows)
        test_x = encode(test_windows)
        y = np.asarray(train_y, dtype=float)
        actual = np.asarray(test_y, dtype=float)

        scale = train_x.std(axis=0)
        scale[scale == 0.0] = 1.0
        train_z = train_x / scale
        test_z = test_x / scale
        design = np.column_stack((np.ones(len(train_z)), train_z))
        regularizer = np.eye(design.shape[1])
        regularizer[0, 0] = 0.0
        coef = np.linalg.solve(
            design.T @ design + self.ridge * regularizer,
            design.T @ y,
        )
        prediction = np.column_stack((np.ones(len(test_z)), test_z)) @ coef

        shuffled = test_z.copy()
        np.random.default_rng(390001).shuffle(shuffled)
        shuffled_prediction = np.column_stack(
            (np.ones(len(shuffled)), shuffled)
        ) @ coef

        return LatentTrajectoryEvaluationResult(
            len(actual),
            float(np.mean(np.abs(actual))),
            float(np.mean(np.abs(actual - prediction))),
            float(np.mean(np.abs(actual - shuffled_prediction))),
            heldout,
            self.history_length,
            self.components,
        )
