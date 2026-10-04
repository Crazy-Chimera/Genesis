from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np

from .memory import MemoryRecord
from .population_innovation import population_state


@dataclass(frozen=True)
class PopulationCompressedTrajectoryResult:
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


class PopulationCompressedTrajectoryPredictor:
    """PCA-compress population state using training data, then predict innovation."""

    def __init__(
        self,
        components: int = 2,
        history_length: int = 2,
        train_fraction: float = 0.5,
        ridge: float = 1e-6,
        require_consecutive: bool = True,
    ) -> None:
        if components < 1:
            raise ValueError("components must be >= 1")
        if history_length < 2:
            raise ValueError("history_length must be >= 2")
        if not 0.0 < train_fraction < 1.0:
            raise ValueError("train_fraction must be between 0 and 1")
        if ridge < 0.0:
            raise ValueError("ridge must be >= 0")
        self.components = components
        self.history_length = history_length
        self.train_fraction = train_fraction
        self.ridge = ridge
        self.require_consecutive = require_consecutive

    def evaluate(self, records: Iterable[MemoryRecord]) -> PopulationCompressedTrajectoryResult:
        by_tick: dict[int, list[MemoryRecord]] = {}
        for record in records:
            by_tick.setdefault(record.tick, []).append(record)
        ticks = sorted(by_tick)
        if len(ticks) <= self.history_length:
            return PopulationCompressedTrajectoryResult(
                0, 0.0, 0.0, 0.0, 0, self.history_length, self.components
            )

        states = {tick: np.asarray(population_state(by_tick[tick])[1], dtype=float) for tick in ticks}
        coherence = {
            tick: float(np.mean([r.coherence for r in by_tick[tick]]))
            for tick in ticks
        }
        heldout = ticks[0] + max(1, int((ticks[-1] - ticks[0]) * self.train_fraction))

        train_windows: list[tuple[int, ...]] = []
        train_y: list[float] = []
        test_windows: list[tuple[int, ...]] = []
        test_y: list[float] = []

        for i in range(self.history_length, len(ticks)):
            window = tuple(ticks[i - self.history_length:i])
            target = ticks[i]
            check = window + (target,)
            if self.require_consecutive and any(
                check[j + 1] != check[j] + 1 for j in range(len(check) - 1)
            ):
                continue
            delta = coherence[target] - coherence[window[-1]]
            if target < heldout:
                train_windows.append(window)
                train_y.append(delta)
            else:
                test_windows.append(window)
                test_y.append(delta)

        if not train_windows or not test_windows:
            return PopulationCompressedTrajectoryResult(
                0, 0.0, 0.0, 0.0, heldout, self.history_length, self.components
            )

        train_ticks = sorted({tick for window in train_windows for tick in window})
        base = np.asarray([states[tick] for tick in train_ticks], dtype=float)
        mean = base.mean(axis=0)
        centered = base - mean
        _, _, vt = np.linalg.svd(centered, full_matrices=False)
        k = min(self.components, vt.shape[0])
        basis = vt[:k].T

        def encode(window: tuple[int, ...]) -> tuple[float, ...]:
            return tuple(
                value
                for tick in window
                for value in ((states[tick] - mean) @ basis)
            )

        train = np.asarray([encode(w) for w in train_windows], dtype=float)
        test = np.asarray([encode(w) for w in test_windows], dtype=float)
        y = np.asarray(train_y, dtype=float)

        xmean = train.mean(axis=0)
        xscale = train.std(axis=0)
        xscale[xscale == 0.0] = 1.0
        design = np.column_stack((np.ones(len(train)), (train - xmean) / xscale))
        reg = np.eye(design.shape[1])
        reg[0, 0] = 0.0
        coef = np.linalg.solve(
            design.T @ design + self.ridge * reg,
            design.T @ y,
        )
        prediction = np.column_stack(
            (np.ones(len(test)), (test - xmean) / xscale)
        ) @ coef

        shuffled = test.copy()
        np.random.default_rng(390001).shuffle(shuffled)
        shuffled_prediction = np.column_stack(
            (np.ones(len(shuffled)), (shuffled - xmean) / xscale)
        ) @ coef

        actual = np.asarray(test_y, dtype=float)
        return PopulationCompressedTrajectoryResult(
            len(actual),
            float(np.mean(np.abs(actual))),
            float(np.mean(np.abs(actual - prediction))),
            float(np.mean(np.abs(actual - shuffled_prediction))),
            heldout,
            self.history_length,
            self.components,
        )
