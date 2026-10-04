from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np

from .memory import MemoryRecord
from .state_innovation import combined_state


@dataclass(frozen=True)
class CompressedTrajectoryResult:
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


class CompressedStateTrajectoryPredictor:
    """Predict coherence innovation from PCA-compressed non-coherence trajectories."""

    def __init__(
        self,
        history_length: int = 3,
        components: int = 16,
        train_fraction: float = 0.5,
        ridge: float = 1e-3,
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
        self.history_length = history_length
        self.components = components
        self.train_fraction = train_fraction
        self.ridge = ridge
        self.require_consecutive = require_consecutive

    def evaluate(self, records: Iterable[MemoryRecord]) -> CompressedTrajectoryResult:
        ordered = sorted(records, key=lambda item: (item.tick, item.identity))
        if not ordered:
            return CompressedTrajectoryResult(
                0, 0.0, 0.0, 0.0, 0, self.history_length, self.components
            )

        min_tick, max_tick = ordered[0].tick, ordered[-1].tick
        heldout = min_tick + max(1, int((max_tick - min_tick) * self.train_fraction))
        groups: dict[int, list[MemoryRecord]] = {}
        for item in ordered:
            groups.setdefault(item.identity, []).append(item)

        train_windows: list[np.ndarray] = []
        train_y: list[float] = []
        test_windows: list[np.ndarray] = []
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
                matrix = np.asarray([combined_state(x) for x in window], dtype=float)
                delta = target.coherence - window[-1].coherence
                if target.tick < heldout:
                    train_windows.append(matrix)
                    train_y.append(delta)
                else:
                    test_windows.append(matrix)
                    test_y.append(delta)

        if not train_windows or not test_windows:
            return CompressedTrajectoryResult(
                0, 0.0, 0.0, 0.0, heldout, self.history_length, self.components
            )

        # Fit the representation only on training states.
        state_matrix = np.concatenate(train_windows, axis=0)
        mean = state_matrix.mean(axis=0)
        centered = state_matrix - mean
        _, singular_values, vh = np.linalg.svd(centered, full_matrices=False)
        rank = min(self.components, vh.shape[0])
        basis = vh[:rank]

        def encode(windows: list[np.ndarray]) -> np.ndarray:
            rows = []
            for window in windows:
                latent = (window - mean) @ basis.T
                rows.append(latent.reshape(-1))
            return np.asarray(rows, dtype=float)

        train = encode(train_windows)
        test = encode(test_windows)
        y = np.asarray(train_y, dtype=float)

        scale = train.std(axis=0)
        scale[scale == 0.0] = 1.0
        normalized = train / scale
        design = np.column_stack((np.ones(len(train)), normalized))
        regularizer = np.eye(design.shape[1])
        regularizer[0, 0] = 0.0
        coefficients = np.linalg.solve(
            design.T @ design + self.ridge * regularizer,
            design.T @ y,
        )

        prediction = np.column_stack(
            (np.ones(len(test)), test / scale)
        ) @ coefficients

        shuffled = test.copy()
        np.random.default_rng(390001).shuffle(shuffled)
        shuffled_prediction = np.column_stack(
            (np.ones(len(shuffled)), shuffled / scale)
        ) @ coefficients

        actual = np.asarray(test_y, dtype=float)
        return CompressedTrajectoryResult(
            len(actual),
            float(np.mean(np.abs(actual))),
            float(np.mean(np.abs(actual - prediction))),
            float(np.mean(np.abs(actual - shuffled_prediction))),
            heldout,
            self.history_length,
            self.components,
        )
